.. _step1-pyenv:

Step1 - Install Pyenv and Python
==============================================================================
This packer build is to install pyenv on ubuntu.

We would like to install pyenv and have Python3.11 pre installed. Also, we would like to ensure that some cli tools like ``curl``, ``wget``, ``git``, ``unzip``, ``screen`` are installed. Also, we would like to have some Python library like ``awscli``, ``boto3``, ``boto_session_manager``, ``s3pathlib``, ``poetry`` pre installed.

Build time is around 10 minutes on ``t3.2xlarge`` EC2.

See source code at `workflow/s01-pyenv/ <https://github.com/MacHu-GWU/acore_ami-project/blob/main/workflow/s01-pyenv>`_.
