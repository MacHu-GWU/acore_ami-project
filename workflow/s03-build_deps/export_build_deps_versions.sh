#!/bin/bash -e

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pip3.11 install pathlib_mate>=1.3.2,<2.0.0
python3.11 /tmp/export_build_deps_versions.py
