# -*- coding: utf-8 -*-

from pathlib_mate import Path
import pynamodb_mate.api as pm
import awscli_mate.api as awscli_mate
from boto_session_manager import BotoSesManager

import acore_ami.api as acore_ami

dir_here = Path.dir_here(__file__)

# initialize your workspace object
# we set ``dir_root`` to the current directory
ws = acore_ami.Workspace(
    name="aws_ubuntu",
    dir_root=dir_here,
)

# initialize your workflow parameter object with values
# you may read sensitive data from external store, such as AWS SSM Parameter Store
path_workflow_param = dir_here.joinpath("workflow_param.json")
workflow_param = acore_ami.WorkflowParam.from_json_file(path_workflow_param)

bsm = BotoSesManager(profile_name=workflow_param.aws_profile)
aws_cli_config = awscli_mate.AWSCliConfig()
aws_cli_config.set_profile_as_default(workflow_param.aws_profile)

for ami_data in acore_ami.AmiData.query_by_workflow(
    workflow_id=workflow_param.workflow_id,
    # workflow_id="you can also hard code it here",
):
    print(
        f"{ami_data.workflow_id = }, "
        f"{ami_data.step_id = }, "
        f"{ami_data.ami_id = }, "
        f"{ami_data.ami_name = }, "
        f"{ami_data.create_at = }."
    )
