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


def _sigstore_python(*args):
    return ["python", "-m", "sigstore", "sign", *args]


def _fatal_help(msg):
    print(f"::error::❌ {msg}")
    sys.exit(1)


inputs = sys.argv[1].split()
summary = Path(os.getenv("GITHUB_STEP_SUMMARY")).open("a")

# The arguments we pass into `sigstore-python` get built up in this list.
sigstore_python_args = []

# The environment variables that we apply to `sigstore-python`.
sigstore_python_env = {}

# The signing artifacts we've generated.
signing_artifact_paths = []

if _DEBUG:
    sigstore_python_env["SIGSTORE_LOGLEVEL"] = "DEBUG"

client_id = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_CLIENT_ID")
if client_id != "":
    sigstore_python_args.extend(["--oidc-client-id", client_id])

client_secret = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_CLIENT_SECRET")
if client_secret != "":
    sigstore_python_args.extend(["--oidc-client-secret", client_secret])

if os.getenv("GHA_SIGSTORE_PYTHON_NO_DEFAULT_FILES", "false") != "false":
    sigstore_python_args.append("--no-default-files")

output_signature = os.getenv("GHA_SIGSTORE_PYTHON_OUTPUT_SIGNATURE")
if output_signature != "":
    sigstore_python_args.extend(["--output-signature", output_signature])

output_certificate = os.getenv("GHA_SIGSTORE_PYTHON_OUTPUT_CERTIFICATE")
if output_certificate != "":
    sigstore_python_args.extend(["--output-certificate", output_certificate])

if os.getenv("GHA_SIGSTORE_PYTHON_OVERWRITE", "false") != "false":
    sigstore_python_args.append("--overwrite")

fulcio_url = os.getenv("GHA_SIGSTORE_PYTHON_FULCIO_URL")
if fulcio_url != "":
    sigstore_python_args.extend(["--fulcio-url", fulcio_url])

rekor_url = os.getenv("GHA_SIGSTORE_PYTHON_REKOR_URL")
if rekor_url != "":
    sigstore_python_args.extend(["--rekor-url", rekor_url])

ctfe = os.getenv("GHA_SIGSTORE_PYTHON_CTFE")
if ctfe != "":
    sigstore_python_args.extend(["--ctfe", ctfe])

rekor_root_pubkey = os.getenv("GHA_SIGSTORE_PYTHON_REKOR_ROOT_PUBKEY")
if rekor_root_pubkey != "":
    sigstore_python_args.extend(["--rekor-root-pubkey", rekor_root_pubkey])

oidc_issuer = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_ISSUER")
if oidc_issuer != "":
    sigstore_python_args.extend(["--oidc-issuer", oidc_issuer])

if os.getenv("GHA_SIGSTORE_PYTHON_STAGING", "false") != "false":
    sigstore_python_args.append("--staging")

for input_ in inputs:
    # Forbid things that look like flags. This isn't a security boundary; just
    # a way to prevent (less motivated) users from breaking the action on themselves.
    if input_.startswith("-"):
        _fatal_help(f"input {input_} looks like a flag")

    files = [Path(f).resolve() for f in glob(input_)]

    for file_ in files:
        if not file_.is_file():
            _fatal_help(f"input {file_} does not look like a file")
        signing_artifact_paths.extend([f"{file_}.crt", f"{file_}.sig"])

    sigstore_python_args.extend(files)

_debug(f"running: sigstore-python {[str(a) for a in sigstore_python_args]}")

status = subprocess.run(
    _sigstore_python(*sigstore_python_args),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env={**os.environ, **sigstore_python_env},
)

_debug(status.stdout)

if status.returncode == 0:
    _log("🎉 sigstore-python exited successfully")
else:
    _log("❌ sigstore-python failed to sign package")

_summary(
    """
<details>
<summary>
    Raw `sigstore-python` output
</summary>

```
    """
)
_log(status.stdout)
_summary(
    """
```
</details>
    """
)

# Now signal to the remaining steps that we've generated the following signing artifacts.
#
# Find the path to the GitHub env file.
gh_env = os.getenv("GITHUB_ENV")
assert gh_env is not None

# The GitHub env file is append only.
with open(gh_env, "a") as f:
    # Multiline outputs must match the following syntax:
    #
    # {name}<<{delimiter}
    # {value}
    # {delimiter}
    f.write(
        "GHA_SIGSTORE_PYTHON_SIGNING_ARTIFACTS<<EOF"
        + os.linesep
        + os.linesep.join(signing_artifact_paths)
        + os.linesep
        + "EOF"
    )

sys.exit(status.returncode)
