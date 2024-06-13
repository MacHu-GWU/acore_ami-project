Overview
==============================================================================
本章主要介绍了本项目相关的 AMI 的基本概览.


Choose the Base Image
------------------------------------------------------------------------------
注: 这段文档写于 2023-03-35.

这篇文档讨论了为 Wserver 这个项目如何选择 Base AMI.

- **OS**: 首先根据 `Azerothecore 的这篇 Linux Requirement 的官方文档 <https://www.azerothcore.org/wiki/linux-requirements>`_, 教程是基于 Ubuntu 20.04 LTS 的, 所以我们最好跟官方文档保持一致, 我们选择 Ubuntu 20.04 LTS.
- **CPU Architect**: 首先我们只考虑 Linux 服务器, 目前市场上有 `x86_64 <https://en.wikipedia.org/wiki/X86-64>`_ (这是一套指令集, 和 AMD64 是一个东西) 和 ARM 两种. ARM 功耗低省钱, 在 AWS 上 ARM 比 X86 要便宜 20% 左右, 但是很多主流软件都只有 X86 平台上的预编译版本, 而没有 ARM 的. 而对于一个游戏服务器来说, 稳定, 可重复, 可靠 要更重要. **所以我们选择 X86_64 (AMD64)**.

在 AWS 的 AMI Catalog (清单) 上我们可以看到 Ubuntu 官方给出的 AMI Name 遵循着这样的规则 ``ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-YYMMDD``, 其中 ``focal`` 是 Ubuntu 20.X 的版本名称, 而 ``YYMMDD`` 是发布日期, 例如 ``20230207``. 所以我们选择这个 AMI 作为我们的 root base AMI.

.. note::

    ``ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-YYMMDD`` Details

    - python: 3.8


AMI Building Order
------------------------------------------------------------------------------
由于整个 AMI 构建过程包含很多步骤, 如果我们将这些步骤放在一个 packer build 中进行, 那么出错的概率就会很高, 而且构建时间也会很长. 所以比较工程化的做法是将其分拆成多个小步骤, 每个小步骤都会输出一个 AMI, 后一个步骤基于前一个步骤来进行构建. 这样我们比较容易对每一个步骤的 AMI 进行检查和定位问题, 反馈速度也会比较快.


AMI Cost Optimization
------------------------------------------------------------------------------
储存 AMI 本身是不花钱的, 但是 AMI 是构建与 EBS Snapshot 之上, 而 EBS 收费的. 具体费用可以查看 `EBS Pricing <https://aws.amazon.com/ebs/pricing/>`_, 写本文的时候的价格是 $0.05/GB Month.

魔兽世界服务器上的文件有两个部分比较大:

1. 地图数据, zip 包 + 解压后一共约 5G.
2. 服务器源码 + 编译后的服务器大约有 1.5G (主要是 SQL 文件).

其中地图文件是可以存在 S3 上, 然后在服务器运行的时候下载下来的, 没有必要塞在 AMI 里. 这里我们做一个简单的计算, 看看是存在 AMI 里还是存在 S3 上更划算.

根据 `S3 Pricing <https://aws.amazon.com/s3/pricing/?p=pm&c=s3&z=4>`_, S3 存储是 $0.023/GB Month, 而将数据从 S3 下载到位于同一个 Region 的 EC2 上是不花钱的. 鉴于 S3 存储比 EBS Snapshot 的存储便宜, 所以存在 S3 上更划算. **但是我们的数据量并不大, 相比之下对我来说等待时间更重要, 所以我们选择将地图数据存在 AMI 里**.


.. _ami-manifest:

AMI Manifest
------------------------------------------------------------------------------
前面介绍了, 我们会将 AMI 的构建过程拆成多个小步骤. 本节详细介绍了每个小步骤的 AMI 的名称, 以及每个步骤我们要做什么 (本节是一个比较概括的介绍, 关于每一步安装了哪些软件, 修改了哪些配置, 请参考对应的代码). 总体来说, 越是更新频率低的部分我们就越先构建. 例如 Python Runtime 大概率我们是不需要重新构建的, 所以我们放在第一步. 而服务器编译是要频繁更新的, 所以我们放在最后一步.

1. ``pyenv``: 在 Root Base Image 上安装了 pyenv 并且安装了 Python, 一些 Python 包, 以及一些常用工具.
2. ``mysql``: 安装了某个具体的 MySQL 版本.
3. ``build_deps``: 参考 `Azerothcore 的 Linux Requirement <https://www.azerothcore.org/wiki/linux-requirements>`_, 预安装了 build 服务器核心的所有编译工具, 其中包括 MySQL 服务器以及客户端.
4. ``server_data``: 包含了从 `wowgaming GitHub <https://github.com/wowgaming/client-data/releases/>`_ 上下载下来的最新地图数据, 由于这个数据非常大, 并且更新频率不高. 而之后我们需要频繁的重新从最新的源码构建服务器, 如果每次都要包含地图数据, 那么创建 AMI (snapshot) 的时间就会变得很长, 所以我们预先将这一步的结果缓存下来.
5. ``built_core``: 包含了已经从源码构建好的服务器核心, 但还没有对服务器进行配置.


MySQL Version
------------------------------------------------------------------------------
根据 `Azerothcore 的 Linux Requirements <https://www.azerothcore.org/wiki/linux-requirements>`_ 文档, 推荐的 MySQL 版本是 8.X. 并且 AWS RDS 也对 8.X 版本支持较为良好, 所以我们选用 8.X. 这里由于历史原因, 我们已经在生产环境中运行的数据库是 8.0.28 版本, 所以我们选择了这个版本.

关于 MySQL 版本跟 build AMI 相关的内容还请参考 ``s02_mysql/README.rst`` 文件, 里面讲的很详细, 这里不进行赘述.
