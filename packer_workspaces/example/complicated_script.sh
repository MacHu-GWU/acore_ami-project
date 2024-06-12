#!/bin/bash
#
# This is an example script to run arbitrary complicated provisioning logics
# in Python. Basically, you can put your provisioning logics in a Python library
# (not just a script, but a library that split logics into modules and import
# each other). Then you can use this script to:
#
# 1. clone the repo from git
# 2. create Python virtualenv and install dependencies
# 3. run your provisioning script

# enable pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# verify availability of python versions
pyenv versions

# install aws cli
pip3.8 install awscli --disable-pip-version-check
# install grc cli so we can git clone from codecommit
pip3.8 install git-remote-codecommit --disable-pip-version-check
# rehash pyenv so it will add awscli and grc to the path
pyenv rehash

# clone the git repo that contains your automation scripts
git clone https://github.com/MacHu-GWU/acore_ami-project

# the current dir will be changed for all the following commands
cd acore_ami-project || exit

# create the virtualenv and install dependencies via poetry
pip3.8 install --disable-pip-version-check virtualenv
virtualenv -p python3.8 .venv
./.venv/bin/pip install -r requirements.txt

# now you can use your virtualenv to run any complicated script
./.venv/bin/python ./packer_workspaces/example/complicated_script.py
