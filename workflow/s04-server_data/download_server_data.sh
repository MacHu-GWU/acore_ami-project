#!/bin/bash -e

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pip install pathlib_mate
python /tmp/download_server_data.py
