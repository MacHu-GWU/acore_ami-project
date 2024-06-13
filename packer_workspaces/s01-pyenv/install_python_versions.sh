#!/bin/bash -e

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pyenv install 3.10.10
pyenv global 3.10.10
pyenv rehash

pip3.10 install pip --upgrade
pip3.10 install virtualenv --upgrade
pip3.10 install "awscli>=1.32.117,<2.0.0"
pip3.10 install "botocore>=1.33.13,<2.0.0"
pip3.10 install "boto3>=1.33.13,<2.0.0"
pip3.10 install "boto_session_manager>=1.7.2<2.0.0"
pip3.10 install "s3pathlib>=2.1.2,<3.0.0"
pip3.10 install "poetry==1.6.1"
pip3.10 install "tomli==2.0.0"
pip3.10 install "fire==0.5.0"
pip3.10 install "rich==12.6.0"
pip3.10 install "colorama==0.4.6"
pip3.10 install "git-remote-codecommit==1.17"
pyenv rehash

# verify
echo "Verify installed Python and libraries"
pyenv versions
python3.10 --version
aws --version
poetry --version
