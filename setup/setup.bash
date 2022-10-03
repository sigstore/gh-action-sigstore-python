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

# NOTE: This file is meant to be sourced, not executed as a script.
if [[ "${0}" == "${BASH_SOURCE[0]}" ]]; then
  die "Internal error: setup harness was executed instead of being sourced?"
fi

# Check the Python version, making sure it's new enough (3.7+)
# The installation step immediately below will technically catch this,
# but doing it explicitly gives us the opportunity to produce a better
# error message.
vers=$(python -V | cut -d ' ' -f2)
maj_vers=$(cut -d '.' -f1 <<< "${vers}")
min_vers=$(cut -d '.' -f2 <<< "${vers}")

[[ "${maj_vers}" == "3" && "${min_vers}" -ge 7 ]] || die "Bad Python version: ${vers}"

python -m pip install --requirement "${GITHUB_ACTION_PATH}/requirements.txt"
