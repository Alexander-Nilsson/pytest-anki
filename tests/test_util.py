import json
import socket
from pathlib import Path

import pytest

from pytest_anki._plugin.util import create_json, find_free_port, get_nested_attribute


class TestCreateJson:
    def test_creates_file_with_data(self, tmp_path):
        path = tmp_path / "test.json"
        data = {"key": "value", "num": 42}
        result = create_json(str(path), data)
        assert result == str(path)
        assert path.read_text() == json.dumps(data)

    def test_creates_file_with_path_object(self, tmp_path):
        nested = tmp_path / "nested"
        nested.mkdir()
        path = nested / "test.json"
        data = {"a": [1, 2, 3]}
        result = create_json(path, data)
        assert result == str(path)
        assert path.read_text() == json.dumps(data)

    def test_overwrites_existing_file(self, tmp_path):
        path = tmp_path / "test.json"
        path.write_text("old")
        create_json(str(path), {"new": "data"})
        assert path.read_text() == json.dumps({"new": "data"})

    def test_empty_dict(self, tmp_path):
        path = tmp_path / "empty.json"
        result = create_json(str(path), {})
        assert result == str(path)
        assert path.read_text() == "{}"


class TestGetNestedAttribute:
    def test_simple_attribute(self):
        class Obj:
            x = 10

        assert get_nested_attribute(Obj, "x") == 10

    def test_nested_attribute(self):
        class Inner:
            value = 42

        class Outer:
            inner = Inner()

        assert get_nested_attribute(Outer, "inner.value") == 42

    def test_deeply_nested(self):
        class A:
            x = 1

        class B:
            a = A()

        class C:
            b = B()

        assert get_nested_attribute(C, "b.a.x") == 1

    def test_missing_attribute_default(self):
        class Obj:
            x = 10

        assert get_nested_attribute(Obj, "y", "default") == "default"
        assert get_nested_attribute(Obj, "x.y", "fallback") == "fallback"

    def test_missing_attribute_no_default(self):
        class Obj:
            x = 10

        with pytest.raises(AttributeError):
            get_nested_attribute(Obj, "y")

    def test_empty_attr_string(self):
        class Obj:
            pass

        with pytest.raises(AttributeError):
            get_nested_attribute(Obj, "")


class TestFindFreePort:
    def test_returns_valid_port(self):
        port = find_free_port()
        assert isinstance(port, int)
        assert 1024 <= port <= 65535

    def test_returns_available_port(self):
        port = find_free_port()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("", port))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        finally:
            sock.close()

    def test_returns_different_ports(self):
        ports = {find_free_port() for _ in range(5)}
        assert len(ports) > 1
