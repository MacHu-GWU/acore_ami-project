Step4 - Download Server Data
==============================================================================
See source code at `workflow/s04-server_data/ <https://github.com/MacHu-GWU/acore_ami-project/blob/main/workflow/s04-server_data>`_.


Overview
------------------------------------------------------------------------------
This packer script is to download server data and unzip it. If we do that with following step together, the change of snapshot would be to large and will too long to create.

The total size of the server data is about 1.2GB (zipped) and 3.3GB (unzipped). So we may use the default EBS volume (8GB) as it is.


Build Time
------------------------------------------------------------------------------
Build time is around 5 minutes on ``t3.2xlarge``.


Reference
------------------------------------------------------------------------------
- Downloads data: https://www.azerothcore.org/wiki/server-setup
