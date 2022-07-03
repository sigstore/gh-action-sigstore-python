gh-action-sigstore-python
=========================

[![CI](https://github.com/trailofbits/gh-action-sigstore-python/actions/workflows/ci.yml/badge.svg)](https://github.com/trailofbits/gh-action-sigstore-python/actions/workflows/ci.yml)
[![Self-test](https://github.com/trailofbits/gh-action-sigstore-python/actions/workflows/selftest.yml/badge.svg)](https://github.com/trailofbits/gh-action-sigstore-python/actions/workflows/selftest.yml)

A GitHub Action that uses [`sigstore-python`](https://github.com/sigstore/sigstore-python)
to sign Python packages.

## Index

* [Usage](#usage)
* [Configuration](#configuration)
  * [⚠️ Internal options ⚠️](#internal-options)
* [Licensing](#licensing)
* [Code of Conduct](#code-of-conduct)

## Usage

Simply add `trailofbits/gh-action-sigstore-python` to one of your workflows:

```yaml
jobs:
  selftest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: install
        run: python -m pip install .
      - uses: trailofbits/gh-action-sigstore-python@v0.0.1
        with:
          inputs: file.txt
```

## Configuration

`gh-action-sigstore-python` takes a variety of configuration inputs, most of which are
optional.

### `inputs`

The `inputs` setting controls what files `sigstore-python` signs. At least one input must be
provided.

To sign one or more files:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.1
  with:
    inputs: file0.txt file1.txt file2.txt
```

### `oidc-client-id`

**Default**: `sigstore`

The `oidc-client-id` setting controls the OpenID Connect client ID to provide to the OpenID Connect
Server during OAuth2.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.1
  with:
    inputs: file.txt
    oidc-client-id: alternative-sigstore-id
```

### `oidc-client-secret`

**Default**: Empty (no OpenID Connect client secret provided by default)

The `oidc-client-secret` setting controls the OpenID Connect client secret to provide to the OpenID
Connect Server during OAuth2.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.1
  with:
    inputs: file.txt
    oidc-client-secret: alternative-sigstore-secret
```

### `fulcio-url`

**Default**: `https://fulcio.sigstore.dev`

The `fulcio-url` setting controls the Fulcio instance to retrieve the ephemeral signing certificate
from.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.1
  with:
    inputs: file.txt
    fulcio-url: https://fulcio.sigstage.dev
```

### `rekor-url`

**Default**: `https://rekor.sigstore.dev`

The `rekor-url` setting controls the Rekor instance to upload the file signature to.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.1
  with:
    inputs: file.txt
    rekor-url: https://rekor.sigstage.dev
```

### `oidc-issuer`

**Default**: `https://oauth2.sigstore.dev/auth`

The `oidc-issuer` setting controls the OpenID Connect issuer to retrieve the OpenID Connect token
from.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.1
  with:
    inputs: file.txt
    oidc-issuer: https://oauth2.sigstage.dev/auth
  ```

### Internal options
<details>
  <summary>⚠️ Internal options ⚠️</summary>

  Everything below is considered "internal," which means that it
  isn't part of the stable public settings and may be removed or changed at
  any points. **You probably do not need these settings.**

  All internal options are prefixed with `internal-be-careful-`.

  #### `internal-be-careful-debug`

  **Default**: `false`

  The `internal-be-careful-debug` setting enables additional debug logs,
  both within `sigstore-python` itself and the action's harness code. You can
  use it to debug troublesome configurations.

  Example:

  ```yaml
  - uses: trailofbits/gh-action-sigstore-python@v0.0.1
    with:
      inputs: file.txt
      internal-be-careful-debug: true
  ```

</details>

## Licensing

`gh-action-sigstore-python` is licensed under the Apache 2.0 License.

## Code of Conduct

Everyone interacting with this project is expected to follow the
[sigstore Code of Conduct](https://github.com/sigstore/.github/blob/main/CODE_OF_CONDUCT.md)
