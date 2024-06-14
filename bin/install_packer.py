# -*- coding: utf-8 -*-

"""
详细文档请参考 https://packer-ami-workflow.readthedocs.io/en/latest/02-Install-Packer/index.html
"""

from pathlib import Path
import acore_ami.vendor.packer_ami_workflow.api as paw

packer_installer = paw.PackerInstaller(
    version="1.11.0",
    platform=paw.PlatformEnum.macOS_arm64,
    # platform=paw.PlatformEnum.linux_amd64,
    dir_workspace=Path(__file__).absolute().parent,
)
packer_installer.install()
