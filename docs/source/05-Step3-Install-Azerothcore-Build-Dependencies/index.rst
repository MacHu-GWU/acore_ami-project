Step3 - Install Azerothcore Build Dependencies
==============================================================================
See source code at `workflow/s03-build_deps/ <https://github.com/MacHu-GWU/acore_ami-project/blob/main/workflow/s03-build_deps>`_.

This packer script is to install necessary build dependencies for building the core. NOTE, MySQL is already built in the previous step.

Requirements, as of 2023-03-20:

- Ubuntu >= 20.04 LTS (Focal Fossa)
- MySQL ≥ 5.7.0 (8.x.y is recommended)
- Boost ≥ 1.74
- OpenSSL ≥ 1.0.x
- CMake ≥ 3.16
- Clang ≥ 10

If you use the ubuntu 18, then the max version of a lot of tools are too old, and you cannot update them via ``apt-get``, you have to install them manually, which is too complicated. So I would like to use ubuntu 20 as the base image.

Check the versions::

    # check ubuntu version
    $ lsb_release -a
    No LSB modules are available.
    Distributor ID: Ubuntu
    Description:    Ubuntu 20.04.5 LTS
    Release:        20.04
    Codename:       focal

    # check boost version
    $ dpkg -s libboost-dev | grep 'Version'
    Version: 1.74.0.3ubuntu7

    # check openssl version
    $ openssl version
    OpenSSL 1.1.1f  31 Mar 2020

    # check clang version
    $ clang --version
    Ubuntu clang version 14.0.0-1ubuntu1.1
    Target: x86_64-pc-linux-gnu
    Thread model: posix
    InstalledDir: /usr/bin

    # check cmake version
    $ cmake --version
    cmake version 3.22.1

    CMake suite maintained and supported by Kitware (kitware.com/cmake).

    # check mysql version
    $ mysql --version
    mysql  Ver 8.0.28 for Linux on x86_64 (MySQL Community Server - GPL)

The total size of the installed dependencies is about 1GB. So we may use the default EBS volume (8GB) as it is.

Build time is around 10 minutes on ``t3.2xlarge``.

Reference:

- Linux Requirements: https://www.azerothcore.org/wiki/linux-requirements
