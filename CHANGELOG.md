# Changelog

All notable changes to `gh-action-sigstore-python` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

All versions prior to 3.0.0 are untracked.

## [Unreleased]

## [3.1.0]

`gh-action-sigstore-python` is now compatible with [Rekor v2](https://blog.sigstore.dev/rekor-v2-ga/)
transparency log (but produced signature bundles still contain Rekor v1 entries by default).

### Changed

* The action now uses sigstore-python 4.1. All other dependencies are also updated
  ([#220](https://github.com/sigstore/gh-action-sigstore-python/pull/220))

### Fixed

* Fixed incompatibility with Python 3.14 by upgrading dependencies
  ([#225](https://github.com/sigstore/gh-action-sigstore-python/pull/225))

### Added

* `rekor-version` argument was added to control the Rekor transparency log
  version when signing. The default version in the gh-action-sigstore-python
  3.x series will remain 1 (except when using `staging: true`).
  ([#228](https://github.com/sigstore/gh-action-sigstore-python/pull/228))

## [3.0.1]

### Changed

* The minimum Python version supported by this action is now 3.9
  ([#155](https://github.com/sigstore/gh-action-sigstore-python/pull/155))
* The action's Python dependencies are now fully pinned to specific versions
  ([#165](https://github.com/sigstore/gh-action-sigstore-python/pull/165))

### Fixed

* The `rfc3161-client` dependency has been upgrades to `1.0.3` to resolve
  a security vulnerability
  ([#182](https://github.com/sigstore/gh-action-sigstore-python/pull/182))

## [3.0.0]

### Added

* `inputs` now allows recursive globbing with `**`
  ([#106](https://github.com/sigstore/gh-action-sigstore-python/pull/106))

### Removed

* The following settings have been removed: `fulcio-url`, `rekor-url`,
  `ctfe`, `rekor-root-pubkey`
  ([#140](https://github.com/sigstore/gh-action-sigstore-python/pull/140))
* The following output settings have been removed: `signature`,
  `certificate`, `bundle`
  ([#146](https://github.com/sigstore/gh-action-sigstore-python/pull/146))

### Changed

* `inputs` is now parsed according to POSIX shell lexing rules, improving
  the action's consistency when used with filenames containing whitespace
  or other significant characters
  ([#104](https://github.com/sigstore/gh-action-sigstore-python/pull/104))

* `inputs` is now optional *if* `release-signing-artifacts` is true
  *and* the action's event is a `release` event. In this case, the action
  takes no explicit inputs, but signs the source archives already attached
  to the associated release
  ([#110](https://github.com/sigstore/gh-action-sigstore-python/pull/110))

* The default suffix has changed from `.sigstore` to `.sigstore.json`,
  per Sigstore's client specification
  ([#140](https://github.com/sigstore/gh-action-sigstore-python/pull/140))

* `release-signing-artifacts` now defaults to `true`
  ([#142](https://github.com/sigstore/gh-action-sigstore-python/pull/142))

### Fixed

* The `release-signing-artifacts` setting no longer causes a hard error
  when used under the incorrect event
  ([#103](https://github.com/sigstore/gh-action-sigstore-python/pull/103))

* Various deprecations present in `sigstore-python`'s 2.x series have been
  resolved
  ([#140](https://github.com/sigstore/gh-action-sigstore-python/pull/140))

* This workflow now supports CI runners that use PEP 668 to constrain global
  package prefixes
  ([#145](https://github.com/sigstore/gh-action-sigstore-python/pull/145))

[Unreleased]: https://github.com/sigstore/gh-action-sigstore-python/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/sigstore/gh-action-sigstore-python/compare/v2.1.1...v3.0.0
