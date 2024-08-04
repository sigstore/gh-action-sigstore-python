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
      - uses: sigstore/gh-action-sigstore-python@v3.0.0
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
provided unless [release-signing-artifacts](#release-signing-artifacts) is set to `true` on release events.

To sign one or more files:

```yaml
- uses: sigstore/gh-action-sigstore-python@v3.0.0
  with:
    inputs: file0.txt file1.txt file2.txt
```

The `inputs` argument also supports file globbing:

```yaml
- uses: sigstore/gh-action-sigstore-python@v3.0.0
  with:
    inputs: ./path/to/inputs/*.txt
```

Multiple lines are fine, and whitespace in filenames can also be escaped using
POSIX shell lexing rules:

```yaml
- uses: sigstore/gh-action-sigstore-python@v3.0.0
  with:
    inputs: |
      ./path/to/inputs/*.txt
      ./another/path/foo\ bar.txt
      ./a/third/path/"easier to quote than to escape".txt
```

> [!NOTE]\
> In versions of this action before 2.0.0, the `inputs` setting allowed for shell expansion.
> This was unintentional, and was removed with 2.0.0.

### `identity-token`

**Default**: Empty (the GitHub Actions credential will be used)

The `identity-token` setting controls the OpenID Connect token provided to Fulcio. By default, the
workflow will use the credentials found in the GitHub Actions environment.

```yaml
- uses: sigstore/gh-action-sigstore-python@v3.0.0
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
- uses: sigstore/gh-action-sigstore-python@v3.0.0
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
- uses: sigstore/gh-action-sigstore-python@v3.0.0
  with:
    inputs: file.txt
    oidc-client-secret: alternative-sigstore-secret
```

### `staging`

**Default**: `false`

The `staging` setting controls whether or not `sigstore-python` uses sigstore's staging instances,
instead of the default production instances.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v3.0.0
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
- uses: sigstore/gh-action-sigstore-python@v3.0.0
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
- uses: sigstore/gh-action-sigstore-python@v3.0.0
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
- uses: sigstore/gh-action-sigstore-python@v3.0.0
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
- uses: sigstore/gh-action-sigstore-python@v3.0.0
  with:
    inputs: file.txt
    upload-signing-artifacts: true
```

### `release-signing-artifacts`

**Default**: `true`

The `release-signing-artifacts` setting controls whether or not `sigstore-python`
uploads signing artifacts to the release publishing event that triggered this run.
This setting has no effect on non-`release` events.

If enabled, this setting also re-uploads and signs GitHub's default source code artifacts,
as they are not guaranteed to be stable.

Requires the [`contents: write` permission](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token).

Example:

```yaml
permissions:
  contents: write

# ...

- uses: sigstore/gh-action-sigstore-python@v3.0.0
  with:
    inputs: file.txt
    release-signing-artifacts: true
```

On release events, it is also valid to have no explicit inputs. When used on release
events, this action will sign any pre-existing release artifacts:

```yaml
permissions:
  contents: write

# ...

# no explicit settings needed, signs all pre-existing release artifacts
- uses: sigstore/gh-action-sigstore-python@v2.1.1
```

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
