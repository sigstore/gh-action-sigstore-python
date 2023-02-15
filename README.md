gh-action-sigstore-python
=========================

[![CI](https://github.com/sigstore/gh-action-sigstore-python/actions/workflows/ci.yml/badge.svg)](https://github.com/sigstore/gh-action-sigstore-python/actions/workflows/ci.yml)
[![Self-test](https://github.com/sigstore/gh-action-sigstore-python/actions/workflows/selftest.yml/badge.svg)](https://github.com/sigstore/gh-action-sigstore-python/actions/workflows/selftest.yml)

A GitHub Action that uses [`sigstore-python`](https://github.com/sigstore/sigstore-python)
to generate Sigstore signatures.

## Index

* [Usage](#usage)
* [Configuration](#configuration)
  * [⚠️ Internal options ⚠️](#internal-options)
* [Licensing](#licensing)
* [Code of Conduct](#code-of-conduct)

## Usage

Simply add `sigstore/gh-action-sigstore-python` to one of your workflows:

```yaml
jobs:
  selftest:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v3
      - name: install
        run: python -m pip install .
      - uses: sigstore/gh-action-sigstore-python@v1.1.0
        with:
          inputs: file.txt
```

Note: Your workflow **must** have permission to request the OIDC token to authenticate with.
This can be done by setting `id-token: write` on your job (as above) or workflow.

More information about permission settings can be found
[here](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#adding-permissions-settings).

## Configuration

`gh-action-sigstore-python` takes a variety of configuration inputs, most of which are
optional.

### `inputs`

The `inputs` setting controls what files `sigstore-python` signs. At least one input must be
provided.

To sign one or more files:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file0.txt file1.txt file2.txt
```

The `inputs` argument also supports file globbing:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: ./path/to/inputs/*.txt
```

### `identity-token`

**Default**: Empty (the GitHub Actions credential will be used)

The `identity-token` setting controls the OpenID Connect token provided to Fulcio. By default, the
workflow will use the credentials found in the GitHub Actions environment.

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    identity-token: ${{ IDENTITY_TOKEN  }} # assigned elsewhere
```

### `oidc-client-id`

**Default**: `sigstore`

The `oidc-client-id` setting controls the OpenID Connect client ID to provide to the OpenID Connect
Server during OAuth2.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
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
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    oidc-client-secret: alternative-sigstore-secret
```

### `signature`

**Default**: Empty (signature files will get named as `{input}.sig`)

The `signature` setting controls the name of the output signature file. This setting does not work
when signing multiple input files.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    signature: custom-signature-filename.sig
```

However, this example is invalid:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file0.txt file1.txt file2.txt
    signature: custom-signature-filename.sig
```

### `certificate`

**Default**: Empty (certificate files will get named as `{input}.crt`)

The `certificate` setting controls the name of the output certificate file. This setting does not
work when signing multiple input files.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    certificate: custom-certificate-filename.crt
```

However, this example is invalid:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file0.txt file1.txt file2.txt
    certificate: custom-certificate-filename.crt
```

### `bundle`

**Default**: Empty (bundle files will get named as `{input}.sigstore`)

The `bundle` setting controls the name of the output Sigstore bundle. This setting does not work
when signing multiple input files.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    bundle: custom-bundle.sigstore
```

However, this example is invalid:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file0.txt file1.txt file2.txt
    certificate: custom-bundle.sigstore
```

### `fulcio-url`

**Default**: `https://fulcio.sigstore.dev`

The `fulcio-url` setting controls the Fulcio instance to retrieve the ephemeral signing certificate
from. This setting cannot be used in combination with the `staging` setting.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
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
- uses: sigstore/gh-action-sigstore-python@v1.1.0
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
- uses: sigstore/gh-action-sigstore-python@v1.1.0
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
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    ctfe: ./path/to/rekor.pub
```

### `staging`

**Default**: `false`

The `staging` setting controls whether or not `sigstore-python` uses sigstore's staging instances,
instead of the default production instances.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    staging: true
```

### `verify`

**Default**: `false`

The `verify` setting controls whether or not the generated signatures and certificates are
verified with the `sigstore verify` subcommand after all files have been signed.

This is **not strictly necessary** but can act as a smoke test to ensure that all
signing artifacts were generated properly and the signature was properly
submitted to Rekor.

If `verify` is enabled, then you **must** also pass the `verify-cert-identity`
and `verify-oidc-issuer` settings. Failing to pass these will produce an error.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    verify: true
    verify-oidc-issuer: https://some-oidc-issuer.example.com
    verify-cert-identity: some-identity
```

### `verify-cert-identity`

**Default**: Empty

The `verify-cert-identity` setting controls whether to verify the Subject Alternative Name (SAN) of the
signing certificate after signing has taken place. If it is set, `sigstore-python` will compare the
certificate's SAN against the provided value.

This setting only applies if `verify` is set to `true`. Supplying it without `verify: true`
will produce an error.

This setting may only be used in conjunction with `verify-oidc-issuer`.
Supplying it without `verify-oidc-issuer` will produce an error.

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    verify: true
    verify-cert-identity: john.hancock@example.com
    verify-oidc-issuer: https://oauth2.sigstage.dev/auth
```

### `verify-oidc-issuer`

**Default**: `https://oauth2.sigstore.dev/auth`

The `verify-oidc-issuer` setting controls whether to verify the issuer extension of the signing
certificate after signing has taken place. If it is set, `sigstore-python` will compare the
certificate's issuer extension against the provided value.

This setting only applies if `verify` is set to `true`. Supplying it without `verify: true`
will produce an error.

This setting may only be used in conjunction with `verify-cert-identity`.
Supplying it without `verify-cert-identity` will produce an error.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    verify: true
    verify-cert-identity: john.hancock@example.com
    verify-oidc-issuer: https://oauth2.sigstage.dev/auth
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
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    upload-signing-artifacts: true
```

### `release-signing-artifacts`

**Default**: `false`

The `release-signing-artifacts` setting controls whether or not `sigstore-python`
uploads signing artifacts to the release publishing event that triggered this run.

If enabled, this setting also re-uploads and signs GitHub's default source code artifacts,
as they are not guaranteed to be stable.

By default, no release assets are uploaded.

Requires the [`contents: write` permission](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token).

Example:

```yaml
permissions:
  contents: write

# ...

- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    release-signing-artifacts: true
```

### `bundle-only`

**Default**: `false`

The `bundle-only` setting controls whether or not `sigstore-python` uploads `.crt`
or `.sig` artifacts.

This setting affects the behavior of the `upload-signing-artifacts` and `release-signing-artifacts`
settings. If neither of those settings are specified, this setting has no effect.

By default, `.crt` and `.sig` artifacts are uploaded. If enabled, only the `.sigstore`
signing artifact is uploaded.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v1.1.0
  with:
    inputs: file.txt
    upload-signing-artifacts: true
    bundle-only: true
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
  - uses: sigstore/gh-action-sigstore-python@v1.1.0
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

## Security

Should you discover any security issues, please refer to sigstore's [security
process](https://github.com/sigstore/.github/blob/main/SECURITY.md).

## Info

`gh-action-sigstore-python` is developed as part of the [`sigstore`](https://sigstore.dev) project.

We also use a [slack channel](https://sigstore.slack.com)!
Click [here](https://join.slack.com/t/sigstore/shared_invite/zt-mhs55zh0-XmY3bcfWn4XEyMqUUutbUQ) for the invite link.
