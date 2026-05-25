# Changelog

All notable changes to `scitex-capture` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.4] - 2026-05-26

- De-mock entire test suite: replace all unittest.mock/patch with real
  collaborators (hand-rolled worker subclasses, tmp_path fixtures, real
  subprocesses for PIL-absence and failure paths).
- Test quality: enforce AAA markers, descriptive test names, one-assert
  per test across all test files.
- All 252 tests pass with zero mocks.

## [0.1.3] - 2026-05-15

- Initial public release.
- Fix: route every write under `$SCITEX_DIR/capture/runtime/<category>/`.

## [0.1.2]

- Initial CHANGELOG entry — see git log for prior history.
