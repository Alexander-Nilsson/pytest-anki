# pytest-anki
#
# Copyright (C)  2017-2021 Ankitects Pty Ltd and contributors
# Copyright (C)  2017-2019 Michal Krassowski <https://github.com/krassowski>
# Copyright (C)  2026 Alexander Nilsson
# Copyright (C)  2019-2025 Aristotelis P. <https://glutanimate.com/>
#                and contributors (see CONTRIBUTORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.


import sys
import uuid
from argparse import Namespace
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Optional, Tuple
from unittest.mock import Mock

import aqt
from aqt.main import AnkiQt

if TYPE_CHECKING:
    from anki._backend import RustBackend
    from aqt.profiles import ProfileManager as ProfileManagerType

from .addons import (
    create_addon_config,
    install_addon_from_folder,
    install_addon_from_package,
)
from .aniki_compat import get_auto_update_attr
from .anki import AnkiStateUpdate, update_anki_meta_state
from .suppress import AnkiNoiseSuppressor
from .testing import PostUISetupCallbackType, TestAnkiQtInit
from .types import PathLike


def post_ui_setup_callback_factory(
    anki_base_dir: PathLike,
    packed_addons: Optional[List[PathLike]] = None,
    unpacked_addons: Optional[List[Tuple[str, PathLike]]] = None,
    addon_configs: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
    preset_anki_state: Optional[AnkiStateUpdate] = None,
    skip_loading_addons: bool = False,
):
    def post_ui_setup_callback(main_window: AnkiQt):
        """Initialize add-on manager, install add-ons, load add-ons"""
        main_window.addonManager = aqt.addons.AddonManager(main_window)

        if packed_addons:
            for packed_addon in packed_addons:
                install_addon_from_package(
                    addon_manager=main_window.addonManager, addon_path=packed_addon
                )

        if unpacked_addons:
            for package_name, addon_path in unpacked_addons:
                install_addon_from_folder(
                    anki_base_dir=anki_base_dir,
                    package_name=package_name,
                    addon_path=addon_path,
                )

        if addon_configs:
            for package_name, config_values in addon_configs:
                create_addon_config(
                    anki_base_dir=anki_base_dir,
                    package_name=package_name,
                    user_config=config_values,
                )

        if preset_anki_state and preset_anki_state.meta_storage:
            update_anki_meta_state(
                main_window=main_window, anki_state_update=preset_anki_state
            )

        if not skip_loading_addons:
            # Remove stale addon modules from sys.modules so loadAddons()
            # performs a fresh import from the current addons21 directory
            for addon_meta in main_window.addonManager.all_addon_meta():
                if addon_meta.dir_name in sys.modules:
                    del sys.modules[addon_meta.dir_name]
            main_window.addonManager.loadAddons()

    return post_ui_setup_callback


def custom_init_factory(post_ui_setup_callback: PostUISetupCallbackType):
    """Return a replacement for ``AnkiQt.__init__`` for test isolation.

    Delegates to ``TestAnkiQtInit`` behind a closure so the rest of
    ``patch_anki`` doesn't need to change.
    """
    init = TestAnkiQtInit(post_ui_setup_callback)

    def custom_init(
        main_window: AnkiQt,
        app: aqt.AnkiApp,
        profileManager: "ProfileManagerType",
        backend: "RustBackend",
        opts: Namespace,
        args: List[Any],
        **kwargs,
    ):
        init.run(main_window, app, profileManager, backend, opts, args)

    return custom_init


@contextmanager
def patch_anki(
    post_ui_setup_callback: PostUISetupCallbackType,
) -> Iterator[str]:
    """Patch Anki to:
    - allow more fine-grained control of test execution environment
    - enable concurrent testing
    - bypass blocking update dialog
    - silence test-irrelevant diagnostic output
    """
    from anki.utils import checksum
    from aqt import AnkiApp, errors
    from aqt.main import AnkiQt

    old_init = AnkiQt.__init__
    old_key = AnkiApp.KEY

    setup_auto_update_attribute = get_auto_update_attr()

    old_setup_auto_update = getattr(AnkiQt, setup_auto_update_attribute)
    old_maybe_check_for_addon_updates = AnkiQt.maybe_check_for_addon_updates
    old_errorHandler = errors.ErrorHandler

    patched_ankiqt_init = custom_init_factory(
        post_ui_setup_callback=post_ui_setup_callback
    )

    AnkiQt.__init__ = patched_ankiqt_init  # type: ignore[assignment]
    AnkiApp.KEY = "anki" + checksum(str(uuid.uuid4()))
    setattr(AnkiQt, setup_auto_update_attribute, Mock())
    AnkiQt.maybe_check_for_addon_updates = Mock()  # type: ignore[assignment]  # ty: ignore[invalid-assignment]
    errors.ErrorHandler = Mock()  # type: ignore[misc]  # ty: ignore[invalid-assignment]

    noise_suppressor = AnkiNoiseSuppressor()
    noise_suppressor.apply()

    yield AnkiApp.KEY

    AnkiQt.__init__ = old_init  # type: ignore[assignment]  # ty: ignore[invalid-assignment]
    AnkiApp.KEY = old_key  # type: ignore[assignment]
    setattr(AnkiQt, setup_auto_update_attribute, old_setup_auto_update)
    AnkiQt.maybe_check_for_addon_updates = (  # type: ignore[assignment]
        old_maybe_check_for_addon_updates
    )
    errors.ErrorHandler = old_errorHandler  # type: ignore[misc]

    noise_suppressor.restore()


def set_qt_message_handler_installer(message_handler_installer: Callable):
    aqt.qInstallMessageHandler = message_handler_installer  # type: ignore[assignment]  # ty: ignore[invalid-assignment]
