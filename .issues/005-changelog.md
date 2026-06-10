# Add CHANGELOG.md

## Summary

The project has no `CHANGELOG.md` file. Users tracking the v2 development (or upgrading from 1.x) need to read the git log to understand what changed between releases.

## What's needed

A `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/) format, covering:

- All v2 releases (2.0.0-dev.1 through 2.0.2)
- Notable breaking changes from v1
- Migration-relevant entries

## Suggested sections per release

- Added (new features)
- Changed (changes in existing functionality)
- Deprecated (soon-to-be removed features)
- Removed (removed features)
- Fixed (bug fixes)
- Security (vulnerability fixes)

## Implementation

Can be populated from the existing git log and the migration guide already in the README. Future changes should be enforced via a `.changelog/` fragment directory or manual update on release.
