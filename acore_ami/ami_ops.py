# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from dateutil.parser import parse
import simple_aws_ec2.api as simple_aws_ec2
import aws_console_url.api as aws_console_url
from rich import print as rprint

from .dynamodb import AmiData

if T.TYPE_CHECKING:  # pragma: no cover
    # do pip install "boto3_stubs[ec2]
    from mypy_boto3_ec2.client import EC2Client


def pprint_image_list(images: T.List[simple_aws_ec2.Image]):
    records = [
        dict(
            id=image.id,
            name=image.name,
            state=image.state,
            creation_date=image.creation_date,
            deprecation_time=image.deprecation_time,
        )
        for image in images
    ]
    rprint(records)


def find_root_base_ami(
    ec2_client: "EC2Client",
    source_ami_name: str,
    source_ami_owner_account_id: str,
) -> T.List[simple_aws_ec2.Image]:
    """
    Find the root base ami that is used to build the acore ami. Usually,
    the root base ami is the latest official ubuntu image.
    """
    iter_proxy = simple_aws_ec2.Image.query(
        ec2_client=ec2_client,
        executable_users=["all"],
        filters=[
            dict(Name="owner-id", Values=[source_ami_owner_account_id]),
            dict(Name="name", Values=[source_ami_name]),
            # we use x86_64 only in this project
            dict(Name="architecture", Values=["x86_64"]),
            dict(Name="state", Values=["available"]),
        ],
    )
    images = list()
    for image in iter_proxy:
        images.append(image)
    # sort images, latest image first
    images = list(sorted(images, key=lambda x: x.creation_date, reverse=True))
    return images


def find_newly_built_ami(
    ec2_client: "EC2Client",
    ami_name: str,
) -> simple_aws_ec2.Image:
    image = simple_aws_ec2.Image.query(
        ec2_client=ec2_client,
        filters=[
            dict(Name="name", Values=[ami_name]),
            dict(Name="state", Values=["available"]),
        ],
    ).one()
    return image


def tag_image(
    ec2_client: "EC2Client",
    image_name: str,
    tags: T.Optional[T.Dict[str, str]] = None,
) -> str:
    """
    :param bsm: BotoSesManager
    :param image_name: The unique name of the image that can be used to locate the ami id
    """
    # find image id
    image = simple_aws_ec2.Image.query(
        ec2_client=ec2_client,
        filters=[
            dict(Name="name", Values=[image_name]),
            dict(Name="state", Values=["available"]),
        ],
    ).one()
    image_id = image.id

    # update tags
    create_tags_kwargs = dict(
        Resources=[
            image_id,
        ]
    )
    if tags:
        create_tags_kwargs["Tags"] = [dict(Key=k, Value=v) for k, v in tags.items()]

    # create tags will overwrite the existing tags
    ec2_client.create_tags(**create_tags_kwargs)
    return image_id


def create_dynamodb_item_for_new_image(
    ec2_client: "EC2Client",
    aws_region: str,
    workflow_id: str,
    step_id: str,
    new_ami_name: str,
    base_ami_id: str,
    base_ami_name: str,
    root_base_ami_id: str,
    root_base_ami_name: str,
    metadata: dict,
):
    new_image = find_newly_built_ami(
        ec2_client=ec2_client,
        ami_name=new_ami_name,
    )

    aws_console = aws_console_url.AWSConsole(aws_region=aws_region)
    url = aws_console.ec2.get_ami(image_id_or_arn=new_image.id)

    print(f"preview AMI: {url}")

    ami_data = AmiData(
        workflow_id=workflow_id,
        step_id=step_id,
        ami_id=new_image.id,
        ami_name=new_ami_name,
        create_at=parse(new_image.creation_date),
        aws_console_url=url,
        base_ami_id=base_ami_id,
        base_ami_name=base_ami_name,
        root_base_ami_id=root_base_ami_id,
        root_base_ami_name=root_base_ami_name,
        details=dataclasses.asdict(new_image),
        metadata=metadata,
    )
    ami_data.save()

    print(f"DynamoDB item: {ami_data.item_detail_console_url}")
