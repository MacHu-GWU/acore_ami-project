# -*- coding: utf-8 -*-

import typing as T
import subprocess
import dataclasses
from functools import cached_property

import jinja2
from pathlib_mate import Path
from boto_session_manager import BotoSesManager
from .vendor.jsonutils import json_loads

from .logger import logger


@dataclasses.dataclass
class BaseParam:
    @classmethod
    def from_json_file(cls, path):
        """
        Load the parameter object from a json file.
        """
        data = json_loads(text=Path(path).read_text())
        return cls(**data)


@dataclasses.dataclass
class WorkflowParam(BaseParam):
    """
    The workflow level parameter object. The parameters here are common values
    for all steps.

    :param workflow_id:
    :param aws_profile: The AWS profile name to use.
    :param aws_tags: The AWS tags to apply to the AMI.
    :param vpc_name: The VPC name where the packer build will run.
    :param is_default_vpc: are we using default VPC? use false or true (string, not boolean).
    :param subnet_name: The Subnet name where the packer build will run.
    :param security_group_name: The Security name where the packer build will use.
    :param ec2_iam_role_name: The IAM role name that the packer build will use.
    :param root_base_ami_name: The name of the root base AMI to use for building this AMI.
        this is only used in step 1.
    :param root_base_ami_owner_account_id: The owner account id of the root base AMI.
    """

    workflow_id: str = dataclasses.field()
    aws_profile: T.Optional[str] = dataclasses.field()
    aws_tags: T.Dict[str, str] = dataclasses.field()
    vpc_name: str = dataclasses.field()
    is_default_vpc: str = dataclasses.field()
    subnet_name: str = dataclasses.field()
    security_group_name: str = dataclasses.field()
    ec2_iam_role_name: str = dataclasses.field()
    root_base_ami_name: str = dataclasses.field()
    root_base_ami_owner_account_id: str = dataclasses.field()

    @cached_property
    def aws_region(self) -> str:
        return BotoSesManager(profile_name=self.aws_profile).aws_region


@dataclasses.dataclass
class StepParam(BaseParam):
    """
    The step level parameter object. The parameters here are specific to each step.

    :param step_id: The step id.
    :param source_ami_id: The source AMI id to use for building this AMI.
    :param output_ami_name: The name of the output AMI.
    """

    step_id: str = dataclasses.field()
    source_ami_id: str = dataclasses.field()
    output_ami_name: str = dataclasses.field()


T_PARAM = T.TypeVar("T_PARAM", bound=BaseParam)


def filter_packer_files(path: Path) -> bool:
    """
    Identify whether it is a ``.pkr.hcl`` or ``.pkrvars.hcl`` file.
    """
    return path.basename.endswith("pkr.hcl") or path.basename.endswith("pkrvars.hcl")


@dataclasses.dataclass
class Workspace:
    """
    :param name: The name of the workspace. This is the prefix of all HCL file.
    :param dir_root: The root directory of the workspace.
    """

    name: str = dataclasses.field()
    dir_root: Path = dataclasses.field()

    @property
    def dir_templates(self) -> Path:
        """
        This is the directory where all the packer template source code are stored.
        """
        return self.dir_root / "templates"

    @property
    def path_pkr_hcl_tpl(self) -> Path:
        """
        The path to the .pkr.hcl jinja2 template file.
        """
        return self.dir_templates / f".pkr.hcl"

    @property
    def path_pkrvars_hcl_tpl(self) -> Path:
        """
        The path to the .pkrvars.hcl  jinja2 template file.
        """
        return self.dir_templates / f".pkrvars.hcl"

    @property
    def path_variables_pkr_hcl_tpl(self) -> Path:
        """
        The path to the .variables.pkr.hcl  jinja2 template file.
        """
        return self.dir_templates / f".variables.pkr.hcl"

    @property
    def path_pkr_hcl(self) -> Path:
        """
        The path to the rendered .pkr.hcl file.
        """
        return self.dir_root / f"{self.name}.pkr.hcl"

    @property
    def path_pkrvars_hcl(self) -> Path:
        """
        The path to the rendered .pkrvars.hcl file.
        """
        return self.dir_root / f"{self.name}.pkrvars.hcl"

    @property
    def path_variables_pkr_hcl(self) -> Path:
        """
        The path to the rendered .variables.pkr.hcl file.
        """
        return self.dir_root / f"{self.name}.variables.pkr.hcl"

    @logger.start_and_end(
        msg="Clean up existing .pkc.hcl and .pkrvars.hcl files",
    )
    def clean_up(self):
        """
        Delete existing .pkc.hcl and .pkrvars.hcl files in the workspace directory.
        """
        for path in self.dir_root.select_file(
            filters=filter_packer_files,
            recursive=False,
        ):
            logger.info(f"remove {path} ...")
            path.remove()

    @logger.start_and_end(
        msg="Render packer template files",
    )
    def render(
        self,
        workflow_param: WorkflowParam,
        step_param: StepParam,
        clean_up: bool = True,
    ):
        """
        Generate all the packer template files in the workspace directory,
        by rendering the jinja2 template with the parameter object.

        :param workflow_param: The :class:`WorkflowParam` object.
        :param step_param: The :class:`StepParam` object.
        :param clean_up: Whether to clean up the existing ``.pkr.hcl`` and ``.pkrvars.hcl`` files.
        """
        if clean_up:
            with logger.nested():
                self.clean_up()

        # render all the packer template files
        for path in self.dir_templates.select_file(
            filters=filter_packer_files,
            recursive=False,
        ):
            path_out = self.dir_root / f"{self.name}{path.basename}"
            logger.info(f"render {path_out} ...")
            path_out.write_text(
                jinja2.Template(path.read_text()).render(
                    workflow_param=workflow_param,
                    step_param=step_param,
                )
            )

    @logger.start_and_end(
        msg="run packer validate",
    )
    def packer_validate(
        self,
        workflow_param: WorkflowParam,
        step_param: StepParam,
        render: bool = True,
        clean_up: bool = True,
    ):
        """
        :param workflow_param: The :class:`WorkflowParam` object.
        :param step_param: The :class:`StepParam` object.
        :param render: Whether to render the jinja2 template before running the command.
        :param clean_up: Whether to clean up the existing ``.pkr.hcl`` and ``.pkrvars.hcl`` files.

        Reference:

        - https://developer.hashicorp.com/packer/docs/commands/validate
        """
        if render:
            with logger.nested():
                self.render(
                    workflow_param=workflow_param,
                    step_param=step_param,
                    clean_up=clean_up,
                )

        args = ["packer", "validate"]
        for path in self.dir_root.select_file(
            filters=lambda p: p.basename.endswith(".pkrvars.hcl"),
            recursive=False,
        ):
            args.append(f"-var-file={path}")

        args.append(f"{self.dir_root}")

        logger.info("run 'packer validate' command:")
        logger.info("packer validate \\\n\t" + " \\\n\t".join(args[2:]))

        with self.dir_root.temp_cwd():
            subprocess.run(args, check=True)

    @logger.start_and_end(
        msg="run packer build",
    )
    def packer_build(
        self,
        workflow_param: WorkflowParam,
        step_param: StepParam,
        render: bool = True,
        clean_up: bool = True,
        dry_run: bool = True,
    ):
        """
        :param workflow_param: The :class:`WorkflowParam` object.
        :param step_param: The :class:`StepParam` object.
        :param render: Whether to render the jinja2 template before running the command.
        :param clean_up: Whether to clean up the existing ``.pkr.hcl`` and ``.pkrvars.hcl`` files.
        """
        if render:
            with logger.nested():
                self.render(
                    workflow_param=workflow_param,
                    step_param=step_param,
                    clean_up=clean_up,
                )

        args = [
            "packer",
            "build",
            "-debug",
        ]

        for path in self.dir_root.select_file(
            filters=lambda p: p.basename.endswith(".pkrvars.hcl"),
            recursive=False,
        ):
            args.append(f"-var-file={path}")

        args.append(f"{self.dir_root}")

        logger.info("run 'packer build' command:")
        logger.info("packer build \\\n\t" + " \\\n\t".join(args[2:]))

        with self.dir_root.temp_cwd():
            if dry_run is False:
                subprocess.run(args, check=True)

    @logger.start_and_end(
        msg="run packer build workflow",
    )
    def run_packer_build_workflow(
        self,
        workflow_param: WorkflowParam,
        step_param: StepParam,
        render: bool = True,
        clean_up: bool = True,
        validate: bool = True,
        dry_run: bool = True,
    ):
        """
        :param workflow_param: The :class:`WorkflowParam` object.
        :param step_param: The :class:`StepParam` object.
        :param render: Whether to render the jinja2 template before running the command.
        :param clean_up: Whether to clean up the existing ``.pkr.hcl`` and ``.pkrvars.hcl`` files.
        :param validate: Whether to run the packer validate command before running the packer build command.
        :param dry_run: Whether to run the command in dry-run mode.
        """
        if render:
            with logger.nested():
                self.render(
                    workflow_param=workflow_param,
                    step_param=step_param,
                    clean_up=clean_up,
                )

        if validate:
            with logger.nested():
                self.packer_validate(
                    workflow_param=workflow_param, step_param=step_param, render=False
                )

        with logger.nested():
            self.packer_build(
                workflow_param=workflow_param,
                step_param=step_param,
                render=False,
                clean_up=False,
                dry_run=dry_run,
            )
