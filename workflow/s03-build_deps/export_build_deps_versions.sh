#!/bin/bash -e

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# with pyenv, pip and python command are using the user installed python version
pip install "pathlib_mate>=1.3.2,<2.0.0"
python /tmp/export_build_deps_versions.py
