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
      - uses: trailofbits/gh-action-sigstore-python@v0.0.2
        with:
          inputs: file.txt
```

Your workflow must have permission to request the OIDC token to authenticate with. This can be done
by having a top-level `permission` setting for your workflow.

```yaml
permissions:
  id-token: write
```

More information about permission settings can be found [here](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#adding-permissions-settings).

## Configuration

`gh-action-sigstore-python` takes a variety of configuration inputs, most of which are
optional.

### `inputs`

The `inputs` setting controls what files `sigstore-python` signs. At least one input must be
provided.

To sign one or more files:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file0.txt file1.txt file2.txt
```

The `inputs` argument also supports file globbing:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: ./path/to/inputs/*.txt
```

### `oidc-client-id`

**Default**: `sigstore`

The `oidc-client-id` setting controls the OpenID Connect client ID to provide to the OpenID Connect
Server during OAuth2.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
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
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    oidc-client-secret: alternative-sigstore-secret
```

### `no-default-files`

**Default**: `false`

The `no-default-files` setting controls whether the default output files (`{input}.sig` and
`{input.crt}`) are emitted.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    no-default-files: true
```

### `output-signature`

**Default**: Empty (signature files will get named as `{input}.sig`)

The `output-signature` setting controls the name of the output signature file. This setting does
not work when signing multiple input files.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    output-signature: custom-signature-filename.sig
```

However, this example is invalid:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file0.txt file1.txt file2.txt
    output-signature: custom-signature-filename.sig
```

### `output-certificate`

**Default**: Empty (certificate files will get named as `{input}.crt`)

The `output-certificate` setting controls the name of the output certificate file. This setting does
not work when signing multiple input files.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    output-certificate: custom-certificate-filename.crt
```

However, this example is invalid:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file0.txt file1.txt file2.txt
    output-certificate: custom-certificate-filename.crt
```

### `overwrite`

**Default**: `false`

The `overwrite` setting controls whether preexisting signature and certificate outputs get
overwritten.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    overwrite: true
```

### `fulcio-url`

**Default**: `https://fulcio.sigstore.dev`

The `fulcio-url` setting controls the Fulcio instance to retrieve the ephemeral signing certificate
from. This setting cannot be used in combination with the `staging` setting.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    fulcio-url: https://fulcio.sigstage.dev
```

### `rekor-url`

**Default**: `https://rekor.sigstore.dev`

The `rekor-url` setting controls the Rekor instance to upload the file signature to. This setting
cannot be used in combination with the `staging` setting.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    rekor-url: https://rekor.sigstage.dev
```

### `ctfe`

**Default**: `ctfe.pub` (the CTFE key embedded in `sigstore-python`)

The `ctfe` setting is a path to a PEM-encoded public key for the CT log. This setting cannot be used
in combination with the `staging` setting.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    ctfe: ./path/to/ctfe.pub
```

### `rekor-root-pubkey`

**Default**: `rekor.pub` (the Rekor key embedded in `sigstore-python`)

The `rekor-root-pubkey` setting is a path to a PEM-encoded public key for Rekor. This setting cannot
be used in combination with `staging` setting.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    ctfe: ./path/to/rekor.pub
```

### `oidc-issuer`

**Default**: `https://oauth2.sigstore.dev/auth`

The `oidc-issuer` setting controls the OpenID Connect issuer to retrieve the OpenID Connect token
from.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    oidc-issuer: https://oauth2.sigstage.dev/auth
```

### `staging`

**Default**: `false`

The `staging` setting controls whether or not `sigstore-python` uses sigstore's staging instances,
instead of the default production instances.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    staging: true
```

### `upload-signing-artifacts`

**Default**: `false`

The `upload-signing-artifacts` setting controls whether or not `sigstore-python` creates
[workflow artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
for the outputs produced by signing operations.

By default, no workflow artifacts are uploaded. When enabled, the default
workflow artifact retention period is used.

Example:

```yaml
- uses: trailofbits/gh-action-sigstore-python@v0.0.2
  with:
    inputs: file.txt
    upload-signing-artifacts: true
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
  - uses: trailofbits/gh-action-sigstore-python@v0.0.2
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
