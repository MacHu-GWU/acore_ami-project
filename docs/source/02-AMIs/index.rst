AMIs
==============================================================================
本章主要介绍了每个 AMI 构建的过程中的具体信息.


.. _packer-build-automation:

Packer Build Automation
------------------------------------------------------------------------------
一个完整的 Packer Build 程序包含这么几个步骤:

1. 准备好运行 ``packer build`` 命令的所有 asset, 例如 ``*.pkr.hcl`` 和 variables 文件.
2. 运行 ``packer build`` 命令, 生成 AMI.
3. 对生成的 AMI 进行管理. 例如你可能需要用一个数据库来记录每个 AMI 的信息, 以便后续的使用.

这里我重点说一下 #1 和 #3.


Prepare Packer Templates
------------------------------------------------------------------------------
`Packer 原生的 Template <https://developer.hashicorp.com/packer/docs/templates/hcl_templates>`_ 本质上相当于一个 declaration (声明式) 的脚本. 这有点类似于 CloudFormation, 它不是面像过程, 而是声明式的. 但是它有着声明式脚本的通用缺点, 自动化程度不高, 参数化系统不够灵活, 你无法基于 parameter 来用 if else, for loop 等对整个 template 的结构进行控制. 所以我在 Template 上又用 `jinja2 <https://jinja.palletsprojects.com/en/3.1.x/>`_ 模板引擎封装了一层 (这跟我初期改进 CloudFormation 流程的做法类似). 具体来说整个开发流程是这样的:

1. 用 jinja2 语言写 hcl 模板. 其中使用一个 ``params`` Python 对象作为所有的 parameter 的 container, 然后用 ``{{ params.parameter_name }}`` 这样的语法来插入参数. 所有的 jinja2 模板都放在 templates 目录下.
2. 在 Python 脚本中生成 params 对象, 至于 params 的数据放在哪里由开发者自己决定. 一般是放在 JSON 里.
3. 用 jinja2 语言 render 最终的 hcl 文件, 并将其放在对应的目录下.

其中在 #1 这一步, 我们有三个文件需要维护:

- ``*.pkr.hcl``: packer template 的主脚本, 定义了 packer build 的逻辑.
- ``*.variables.pkr.hcl``: packer variables 的声明文件. 注意这里只是定义, 而不包含 value. (see https://developer.hashicorp.com/packer/guides/hcl/variables for more information)
- ``*.pkrvars.hcl``: packer variables 的值. packer build 的时候会从这里面读数据.

在编写 ``*.pkr.hcl`` 的时候, 所以直接被 pass 到 template 中的参数 (例如 string replacement) 都需要在 ``*.variables.pkr.hcl`` 中定义. 这样能充分利用 packer 的 declaration 语法记录每个 variable 是用来干什么的. 而如果是用来操作 template 结构的参数我们就不要放在 ``*.variables.pkr.hcl`` 中了. 我认为不应该用 jinja2 template 来完全替代 packer 的 variables 系统, 因为 jinja2 主要是一个 string template engine, 插入值的时候并不会检查类型, 所以我们只用 jinja2 来做 string manipulation, if/else, for loop.

.. dropdown:: .py

    ... 这里放几个例子.


Manage AMIs
------------------------------------------------------------------------------
AWS 官方有很多 AMI API 可以进行 list, get details 等操作. 但是灵活性还是远远不如用数据库来管理 metadata. 所以在这个项目中我们会用 DynamoDB 来管理 AMI 的 metadata, 使得我们可以更方便地操作 AMI.
