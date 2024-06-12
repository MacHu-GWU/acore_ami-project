# -*- coding: utf-8 -*-

import typing as T
import dataclasses
import enum
import pynamodb_mate.api as pm


class StepIdEnum(str, enum.Enum):
    pyenv = "pyenv"
    mysql = "mysql"
    build_deps = "build_deps"
    server_data = "server_data"
    built_core = "built_core"


class StepIdIndex(pm.GlobalSecondaryIndex):
    class Meta:
        index_name = "step_id_index"
        projection = pm.AllProjection()

    step_id = pm.UnicodeAttribute(hash_key=True)
    create_at = pm.UTCDateTimeAttribute(range_key=True)


@dataclasses.dataclass
class Metadata:
    """
    User custom metadata.
    """

    azerothcore_wotlk_commit_id: str = dataclasses.field(default=None)

    def to_dict(self) -> T.Dict[str, T.Any]:
        data = dataclasses.asdict(self)
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_dict(cls, dct: T.Dict[str, T.Any]):
        return cls(**dct)


class AmiData(pm.Model):
    """
    This is the model class for the DynamoDB table `acore_ami_catalog`.

    I usually rebuild the AMI every month. And in each month, I may go through
    step 1, 2, 3, ... all the way to the end, or may start from 3, 4, 5.
    The workflow id is a unique identifier for each month's AMI building process.
    For example, on 2024-01-01, I rebuild the AMI for step 1, 2, 3, 4, 5.
    Then the workflow id is "2024-01-01". And the step id is "pyenv", "mysql",
    "build_deps", "server_data", "built_core".

    :param workflow_id:
    :param step_id:
    :param ami_id:
    :param ami_name:
    :param create_at:
    :param aws_console_url: AWS console url to open the AMI details in the browser.
    :param base_ami_id: this AMI is built on top of which base AMI?
    :param base_ami_name: name of the base AMI.
    :param root_base_ami_id: which AMI we originally start from? Usually it's the
        ubuntu official AMI.
    :param root_base_ami_name: name of the root base AMI.
    :param details: the response of the
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_images.html
        API call.
    :param metadata: user custom metadata
    """

    class Meta:
        # since the AMI is immutable artifacts, there's only one environment for AMI
        # we don't use sbx, tst, prd environment
        table_name = "acore_ami_catalog"
        region = "us-east-1"
        billing_mode = pm.constants.PAY_PER_REQUEST_BILLING_MODE

    workflow_id = pm.UnicodeAttribute(hash_key=True)
    step_id = pm.UnicodeAttribute(range_key=True)
    ami_id = pm.UnicodeAttribute()
    ami_name = pm.UnicodeAttribute()
    create_at = pm.UTCDateTimeAttribute()
    aws_console_url = pm.UnicodeAttribute()
    base_ami_id = pm.UnicodeAttribute()
    base_ami_name = pm.UnicodeAttribute()
    root_base_ami_id = pm.UnicodeAttribute()
    root_base_ami_name = pm.UnicodeAttribute()
    details = pm.JSONAttribute()
    metadata = pm.JSONAttribute()

    @classmethod
    def query_by_workflow(cls, workflow_id: str):
        return list(
            sorted(
                cls.query(hash_key=workflow_id),
                key=lambda x: x.create_at,
                reverse=False,
            )
        )
