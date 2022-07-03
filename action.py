#!/usr/bin/env python3

# action.py: run sigstore-python
#
# most state is passed in as environment variables; the only argument
# is a whitespace-separated list of inputs

import os
import subprocess
import sys
from base64 import b64encode
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


inputs = [Path(p).resolve() for p in sys.argv[1].split()]
summary = Path(os.getenv("GITHUB_STEP_SUMMARY")).open("a")

# The arguments we pass into `sigstore-python` get built up in this list.
sigstore_python_args = []

# The environment variables that we apply to `sigstore-python`.
sigstore_python_env = {}

if _DEBUG:
    sigstore_python_env["SIGSTORE_LOGLEVEL"] = "DEBUG"

client_id = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_CLIENT_ID")
if client_id != "":
    sigstore_python_args.extend(["--oidc-client-id", client_id])

client_secret = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_CLIENT_SECRET")
if client_secret != "":
    sigstore_python_args.extend(["--oidc-client-secret", client_secret])

fulcio_url = os.getenv("GHA_SIGSTORE_PYTHON_FULCIO_URL")
if fulcio_url != "":
    sigstore_python_args.extend(["--fulcio-url", fulcio_url])

rekor_url = os.getenv("GHA_SIGSTORE_PYTHON_REKOR_URL")
if rekor_url != "":
    sigstore_python_args.extend(["--rekor-url", rekor_url])

oidc_issuer = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_ISSUER")
if oidc_issuer != "":
    sigstore_python_args.extend(["--oidc-issuer", oidc_issuer])

for input_ in inputs:
    # Forbid things that look like flags. This isn't a security boundary; just
    # a way to prevent (less motivated) users from breaking the action on themselves.
    if str(input_).startswith("-"):
        _fatal_help(f"input {input_} looks like a flag")

    if not input_.is_file():
        _fatal_help(f"input {input_} does not look like a file")
    sigstore_python_args.append(input_)

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

    with open("/tmp/sigstore-python-output.txt", "r") as io:
        output = io.read()

        # This is really nasty: our output contains multiple lines,
        # so we can't naively stuff it into an output (since this is all done
        # in-channel as a special command on stdout).
        print(f"::set-output name=output::{b64encode(output.encode()).decode()}")

        _summary("```")
        _log(output)
        _summary("```")


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

sys.exit(status.returncode)
