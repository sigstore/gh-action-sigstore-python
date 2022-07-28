#!/usr/bin/env python3

# action.py: run sigstore-python
#
# most state is passed in as environment variables; the only argument
# is a whitespace-separated list of inputs

import os
import subprocess
import sys
from glob import glob
from pathlib import Path

_OUTPUTS = [sys.stderr]
_SUMMARY = Path(os.getenv("GITHUB_STEP_SUMMARY")).open("a")
_RENDER_SUMMARY = os.getenv("GHA_SIGSTORE_PYTHON_SUMMARY", "true") == "true"
_DEBUG = os.getenv("GHA_SIGSTORE_PYTHON_INTERNAL_BE_CAREFUL_DEBUG", "false") != "false"

if _RENDER_SUMMARY:
    _OUTPUTS.append(_SUMMARY)


def _summary(msg):
    if _RENDER_SUMMARY:
        print(msg, file=_SUMMARY)


def _debug(msg):
    if _DEBUG:
        print(f"\033[93mDEBUG: {msg}\033[0m", file=sys.stderr)


def _log(msg):
    for output in _OUTPUTS:
        print(msg, file=output)


def _sigstore_python_sign(*args):
    return ["python", "-m", "sigstore", "sign", *args]


def _sigstore_python_verify(*args):
    return ["python", "-m", "sigstore", "verify", *args]


def _fatal_help(msg):
    print(f"::error::❌ {msg}")
    sys.exit(1)


inputs = sys.argv[1].split()
summary = Path(os.getenv("GITHUB_STEP_SUMMARY")).open("a")

# The arguments we pass into `sigstore-python` get built up in these lists.
sigstore_python_sign_args = []
sigstore_python_verify_args = []

# The environment variables that we apply to `sigstore-python`.
sigstore_python_env = {}

if _DEBUG:
    sigstore_python_env["SIGSTORE_LOGLEVEL"] = "DEBUG"

client_id = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_CLIENT_ID")
if client_id != "":
    sigstore_python_sign_args.extend(["--oidc-client-id", client_id])

client_secret = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_CLIENT_SECRET")
if client_secret != "":
    sigstore_python_sign_args.extend(["--oidc-client-secret", client_secret])

if os.getenv("GHA_SIGSTORE_PYTHON_NO_DEFAULT_FILES", "false") != "false":
    sigstore_python_sign_args.append("--no-default-files")

output_signature = os.getenv("GHA_SIGSTORE_PYTHON_OUTPUT_SIGNATURE")
if output_signature != "":
    sigstore_python_sign_args.extend(["--signature", output_signature])
    sigstore_python_verify_args.extend(["--signature", output_signature])

output_certificate = os.getenv("GHA_SIGSTORE_PYTHON_OUTPUT_CERTIFICATE")
if output_certificate != "":
    sigstore_python_sign_args.extend(["--certificate", output_certificate])
    sigstore_python_verify_args.extend(["--certificate", output_certificate])

if os.getenv("GHA_SIGSTORE_PYTHON_OVERWRITE", "false") != "false":
    sigstore_python_sign_args.append("--overwrite")

fulcio_url = os.getenv("GHA_SIGSTORE_PYTHON_FULCIO_URL")
if fulcio_url != "":
    sigstore_python_sign_args.extend(["--fulcio-url", fulcio_url])

rekor_url = os.getenv("GHA_SIGSTORE_PYTHON_REKOR_URL")
if rekor_url != "":
    sigstore_python_sign_args.extend(["--rekor-url", rekor_url])
    sigstore_python_verify_args.extend(["--rekor-url", rekor_url])

ctfe = os.getenv("GHA_SIGSTORE_PYTHON_CTFE")
if ctfe != "":
    sigstore_python_sign_args.extend(["--ctfe", ctfe])

rekor_root_pubkey = os.getenv("GHA_SIGSTORE_PYTHON_REKOR_ROOT_PUBKEY")
if rekor_root_pubkey != "":
    sigstore_python_sign_args.extend(["--rekor-root-pubkey", rekor_root_pubkey])

oidc_issuer = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_ISSUER")
if oidc_issuer != "":
    sigstore_python_sign_args.extend(["--oidc-issuer", oidc_issuer])

if os.getenv("GHA_SIGSTORE_PYTHON_STAGING", "false") != "false":
    sigstore_python_sign_args.append("--staging")
    sigstore_python_verify_args.append("--staging")

for input_ in inputs:
    # Forbid things that look like flags. This isn't a security boundary; just
    # a way to prevent (less motivated) users from breaking the action on themselves.
    if input_.startswith("-"):
        _fatal_help(f"input {input_} looks like a flag")

    files = [Path(f).resolve() for f in glob(input_)]

    for file_ in files:
        if not file_.is_file():
            _fatal_help(f"input {file_} does not look like a file")

    sigstore_python_sign_args.extend(files)
    sigstore_python_verify_args.extend(files)

_debug(f"running: sigstore-python {[str(a) for a in sigstore_python_sign_args]}")

sign_status = subprocess.run(
    _sigstore_python_sign(*sigstore_python_sign_args),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env={**os.environ, **sigstore_python_env},
)

_debug(sign_status.stdout)

if sign_status.returncode == 0:
    _log("🎉 sigstore-python signing exited successfully")
else:
    _log("❌ sigstore-python failed to sign package")

verify_status = None
if sign_status.returncode == 0:
    verify_status = subprocess.run(
        _sigstore_python_verify(*sigstore_python_verify_args),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, **sigstore_python_env},
    )
    _debug(verify_status.stdout)

if verify_status is None:
    _log("❌ sigstore-python verification skipped due to failed signing")
elif verify_status.returncode == 0:
    _log("🎉 sigstore-python verification exited successfully")
else:
    _log("❌ sigstore-python failed to verify package")


_summary(
    """
<details>
<summary>
    Raw `sigstore-python sign` output
</summary>

```
    """
)
_log(sign_status.stdout)
_summary(
    """
```
</details>
    """
)
if verify_status is not None:
    _summary(
        """
<details>
<summary>
    Raw `sigstore-python verify` output
</summary>

```
        """
    )
    _log(verify_status.stdout)
    _summary(
        """
```
</details>
        """
    )

if sign_status.returncode != 0:
    assert verify_status is None
    sys.exit(sign_status.returncode)
else:
    sys.exit(verify_status.returncode)
