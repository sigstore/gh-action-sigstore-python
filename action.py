#!/usr/bin/env python3

# action.py: run sigstore-python
#
# most state is passed in as environment variables; the only argument
# is a whitespace-separated list of inputs

import os
import string
import subprocess
import sys
from glob import glob
from pathlib import Path

_HERE = Path(__file__).parent.resolve()
_TEMPLATES = _HERE / "templates"

_SUMMARY = Path(os.getenv("GITHUB_STEP_SUMMARY")).open("a")
_RENDER_SUMMARY = os.getenv("GHA_SIGSTORE_PYTHON_SUMMARY", "true") == "true"
_DEBUG = os.getenv("GHA_SIGSTORE_PYTHON_INTERNAL_BE_CAREFUL_DEBUG", "false") != "false"


def _template(name):
    path = _TEMPLATES / f"{name}.md"
    return string.Template(path.read_text())


def _summary(msg):
    if _RENDER_SUMMARY:
        print(msg, file=_SUMMARY)


def _debug(msg):
    if _DEBUG:
        print(f"\033[93mDEBUG: {msg}\033[0m", file=sys.stderr)


def _log(msg):
    print(msg, file=sys.stderr)


def _sigstore_sign(*args):
    return ["python", "-m", "sigstore", "sign", *args]


def _sigstore_verify(*args):
    return ["python", "-m", "sigstore", "verify", *args]


def _fatal_help(msg):
    print(f"::error::❌ {msg}")
    sys.exit(1)


inputs = sys.argv[1].split()
summary = Path(os.getenv("GITHUB_STEP_SUMMARY")).open("a")

# The arguments we pass into `sigstore-python` get built up in these lists.
sigstore_sign_args = []
sigstore_verify_args = []

# The environment variables that we apply to `sigstore-python`.
sigstore_python_env = {}

# Flag to check whether we want enable the verify step.
enable_verify = True

# A list of paths to signing artifacts generated by `sigstore-python`. We want
# to upload these as workflow artifacts after signing.
signing_artifact_paths = []

if _DEBUG:
    sigstore_python_env["SIGSTORE_LOGLEVEL"] = "DEBUG"

identity_token = os.getenv("GHA_SIGSTORE_PYTHON_IDENTITY_TOKEN")
if identity_token != "":
    sigstore_sign_args.extend(["--identity-token", identity_token])

client_id = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_CLIENT_ID")
if client_id != "":
    sigstore_sign_args.extend(["--oidc-client-id", client_id])

client_secret = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_CLIENT_SECRET")
if client_secret != "":
    sigstore_sign_args.extend(["--oidc-client-secret", client_secret])

signature = os.getenv("GHA_SIGSTORE_PYTHON_SIGNATURE")
if signature != "":
    sigstore_sign_args.extend(["--signature", signature])
    sigstore_verify_args.extend(["--signature", signature])

certificate = os.getenv("GHA_SIGSTORE_PYTHON_CERTIFICATE")
if certificate != "":
    sigstore_sign_args.extend(["--certificate", certificate])
    sigstore_verify_args.extend(["--certificate", certificate])

output_signature = os.getenv("GHA_SIGSTORE_PYTHON_SIGNATURE")
if output_signature != "":
    sigstore_sign_args.extend(["--signature", output_signature])
    signing_artifact_paths.append(output_signature)

output_certificate = os.getenv("GHA_SIGSTORE_PYTHON_CERTIFICATE")
if output_certificate != "":
    sigstore_sign_args.extend(["--certificate", output_certificate])
    signing_artifact_paths.append(output_certificate)

fulcio_url = os.getenv("GHA_SIGSTORE_PYTHON_FULCIO_URL")
if fulcio_url != "":
    sigstore_sign_args.extend(["--fulcio-url", fulcio_url])

rekor_url = os.getenv("GHA_SIGSTORE_PYTHON_REKOR_URL")
if rekor_url != "":
    sigstore_sign_args.extend(["--rekor-url", rekor_url])
    sigstore_verify_args.extend(["--rekor-url", rekor_url])

ctfe = os.getenv("GHA_SIGSTORE_PYTHON_CTFE")
if ctfe != "":
    sigstore_sign_args.extend(["--ctfe", ctfe])

rekor_root_pubkey = os.getenv("GHA_SIGSTORE_PYTHON_REKOR_ROOT_PUBKEY")
if rekor_root_pubkey != "":
    sigstore_sign_args.extend(["--rekor-root-pubkey", rekor_root_pubkey])

if os.getenv("GHA_SIGSTORE_PYTHON_STAGING", "false") != "false":
    sigstore_sign_args.append("--staging")
    sigstore_verify_args.append("--staging")

if os.getenv("GHA_SIGSTORE_PYTHON_VERIFY", "false") == "false":
    enable_verify = False

verify_cert_email = os.getenv("GHA_SIGSTORE_PYTHON_VERIFY_CERT_EMAIL")
if verify_cert_email != "":
    sigstore_verify_args.extend(["--cert-email", verify_cert_email])

verify_oidc_issuer = os.getenv("GHA_SIGSTORE_PYTHON_VERIFY_OIDC_ISSUER")
if verify_oidc_issuer != "":
    sigstore_verify_args.extend(["--oidc-issuer", verify_oidc_issuer])

for input_ in inputs:
    # Forbid things that look like flags. This isn't a security boundary; just
    # a way to prevent (less motivated) users from breaking the action on themselves.
    if input_.startswith("-"):
        _fatal_help(f"input {input_} looks like a flag")

    files = [Path(f).resolve() for f in glob(input_)]

    for file_ in files:
        if not file_.is_file():
            _fatal_help(f"input {file_} does not look like a file")
        if "--output_certificate" not in sigstore_sign_args:
            signing_artifact_paths.append(f"{file_}.crt")
        if "--output_signature" not in sigstore_sign_args:
            signing_artifact_paths.append(f"{file_}.sig")

    sigstore_sign_args.extend(files)
    sigstore_verify_args.extend(files)

_debug(f"signing: sigstore-python {[str(a) for a in sigstore_sign_args]}")

sign_status = subprocess.run(
    _sigstore_sign(*sigstore_sign_args),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env={**os.environ, **sigstore_python_env},
)

_debug(sign_status.stdout)

if sign_status.returncode == 0:
    _summary("🎉 sigstore-python signing exited successfully")
else:
    _summary("❌ sigstore-python failed to sign package")

verify_status = None
if sign_status.returncode == 0 and enable_verify:
    _debug(f"verifying: sigstore-python {[str(a) for a in sigstore_verify_args]}")

    verify_status = subprocess.run(
        _sigstore_verify(*sigstore_verify_args),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, **sigstore_python_env},
    )

    _debug(verify_status.stdout)

if verify_status is None:
    # Don't add anything to the summary if verification is disabled.
    if enable_verify:
        _summary("❌ sigstore-python verification skipped due to failed signing")
elif verify_status.returncode == 0:
    _summary("🎉 sigstore-python verification exited successfully")
else:
    _summary("❌ sigstore-python failed to verify package")


_log(sign_status.stdout)
_summary(_template("sigstore-python-sign").substitute(output=sign_status.stdout))

if verify_status is not None:
    _log(verify_status.stdout)
    _summary(
        _template("sigstore-python-verify").substitute(output=verify_status.stdout)
    )

if sign_status.returncode != 0:
    assert verify_status is None
    sys.exit(sign_status.returncode)

# Now populate the `GHA_SIGSTORE_PYTHON_SIGNING_ARTIFACTS` environment variable
# so that later steps know which files to upload as workflow artifacts.
#
# In GitHub Actions, environment variables can be made to persist across
# workflow steps by appending to the file at `GITHUB_ENV`.
with Path(os.getenv("GITHUB_ENV")).open("a") as gh_env:
    # Multiline values must match the following syntax:
    #
    # {name}<<{delimiter}
    # {value}
    # {delimiter}
    gh_env.write(
        "GHA_SIGSTORE_PYTHON_SIGNING_ARTIFACTS<<EOF"
        + os.linesep
        + os.linesep.join(signing_artifact_paths)
        + os.linesep
        + "EOF"
    )


# If signing didn't fail, then we check the verification status, if present.
if verify_status is not None:
    sys.exit(verify_status.returncode)
