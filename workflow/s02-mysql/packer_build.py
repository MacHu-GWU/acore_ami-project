# -*- coding: utf-8 -*-

from pathlib_mate import Path
from acore_ami.builder import AmiBuilder

dir_here = Path.dir_here(__file__)
builder = AmiBuilder.make_builder(dir_step=dir_here)

builder.create_image_manually(instance_id="i-1a2b3c", wait=True)
builder.create_dynamodb_item()
# builder.delete_ami(delete_snapshot=False, skip_prompt=False)
