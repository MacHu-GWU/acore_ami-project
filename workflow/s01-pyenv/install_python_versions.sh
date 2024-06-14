#!/bin/bash -e

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pyenv install 3.11.8
pyenv global 3.11.8
pyenv rehash

pip install pip --upgrade
pip install virtualenv --upgrade
pip install "awscli>=1.32.117,<2.0.0"
pip install "botocore>=1.33.13,<2.0.0"
pip install "boto3>=1.33.13,<2.0.0"
pip install "boto_session_manager>=1.7.2<2.0.0"
pip install "s3pathlib>=2.1.2,<3.0.0"
pip install "poetry==1.6.1"
pip install "tomli==2.0.0"
pip install "fire==0.5.0"
pip install "rich==12.6.0"
pip install "colorama==0.4.6"
pip install "git-remote-codecommit==1.17"
pyenv rehash

# verify
echo "Verify installed Python and libraries"
pyenv versions
python --version
pip --version
virtualenv --version
aws --version
poetry --version
