#!/usr/bin/env bash

# Copyright 2022 The Sigstore Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -eo pipefail

die() {
  echo "::error::${1}"
  exit 1
}

debug() {
  if [[ "${GHA_SIGSTORE_PYTHON_INTERNAL_BE_CAREFUL_DEBUG}" = "true" ]]; then
    echo -e "\033[93mDEBUG: ${1}\033[0m"
  fi
}

debug "Python: $(python -V)"
debug "pip: $(python -m pip --version)"

# NOTE: This file is meant to be sourced, not executed as a script.
if [[ "${0}" == "${BASH_SOURCE[0]}" ]]; then
  die "Internal error: setup harness was executed instead of being sourced?"
fi

# Check the Python version, making sure it's new enough (3.8+)
# The installation step immediately below will technically catch this,
# but doing it explicitly gives us the opportunity to produce a better
# error message.
vers=$(python -V | cut -d ' ' -f2)
maj_vers=$(cut -d '.' -f1 <<< "${vers}")
min_vers=$(cut -d '.' -f2 <<< "${vers}")

[[ "${maj_vers}" == "3" && "${min_vers}" -ge 8 ]] || die "Bad Python version: ${vers}"

# If the user didn't explicitly configure a Python version with
# `actions/setup-python`, then we might be using the distribution's Python and
# therefore be subject to PEP 668. We use a virtual environment unconditionally
# to prevent that kind of confusion.
python -m venv "${GITHUB_ACTION_PATH}/.action-env"

# Annoying: Windows venvs use a different structure, for unknown reasons.
if [[ -d "${GITHUB_ACTION_PATH}/.action-env/bin" ]]; then
  VENV_PYTHON_PATH="${GITHUB_ACTION_PATH}/.action-env/bin/python"
else
  VENV_PYTHON_PATH="${GITHUB_ACTION_PATH}/.action-env/Scripts/python"
fi

"${VENV_PYTHON_PATH}" -m pip install --requirement "${GITHUB_ACTION_PATH}/requirements.txt"

debug "sigstore-python: $("${VENV_PYTHON_PATH}" -m sigstore --version)"

# Finally, propagate VENV_PYTHON_PATH so we can actually kick-start
# the extension from it.
echo "venv-python-path=${VENV_PYTHON_PATH}" >> "${GITHUB_OUTPUT}"
