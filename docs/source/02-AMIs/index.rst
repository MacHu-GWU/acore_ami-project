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


.. _prepare-packer-templates:

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


Packer Build Development Tutorial
------------------------------------------------------------------------------
这一节详细介绍了在这个项目里, 我们是如何开发一个 packer build 脚本的.

**Workflow**

在这个 Repo 的根目录下有一个 `packer_workspace <https://github.com/MacHu-GWU/acore_ami-project/tree/main/packer_workspaces>`_ 目录. 里面包含一个 ``workflow_param.json`` 和一堆文件夹. 里面的目录结构大致长下面这样. 如果你还记得 :ref:`ami-manifest` 中提到的我们将一个 AMI 的多个步骤拆分的策略, 这里的每个子目录就是一个 Step, 多个 Step 合在一起就组成了一个 Workflow. 例如 `example <https://github.com/MacHu-GWU/acore_ami-project/tree/main/packer_workspaces/example>`_ 就是一个作为所有 step 的 workspace 的例子而存在的 Step. 这个 example 跟我们的 wotlk 项目并没有关系, 但是所有有关系的 step 都是用这个 example 作为模板来创建的.

这些 Step 的 packer template 中都会有很多 parameter, 而这里很多 Step 的 parameter 都是一样的. 而 `/packer_workspaces/workflow_param.json <https://github.com/MacHu-GWU/acore_ami-project/blob/main/packer_workspaces/workflow_param.json>`_ 就保存了这些通用的 parameter 的值.

.. code-block::

    /packer_workspaces/
    /packer_workspaces/workflow_param.json
    /packer_workspaces/{step1_workspace}/
    /packer_workspaces/{step2_workspace}/
    /packer_workspaces/.../

.. dropdown:: workflow_param.json

    .. literalinclude:: ../../../packer_workspaces/workflow_param.json
       :language: javascript
       :linenos:

**Step**

下面我们进到一个具体的 Step 里面看看每个 Step 的 packer template 应该怎么写.

下面列出了每个 Step 的 workspace 的目录结构.

.. code-block::

    /workspace/
    /workspace/templates
    /workspace/templates/.pkr.hcl
    /workspace/templates/.pkrvars.hcl
    /workspace/templates/.variables.pkr.hcl
    /workspace/.gitignore
    /workspace/${workflow_name}.pkr.hcl
    /workspace/${workflow_name}.pkrvars.hcl
    /workspace/${workflow_name}.variables.pkr.hcl
    /workspace/complicated_script.py
    /workspace/complicated_script.sh
    /workspace/packer_build.py # <--- 用这个脚本运行 packer build
    /workspace/param.json
    /workspace/README.rst

下面列出了里面比较关键的几个文件:

``.pkr.hcl``: packer template 的主脚本, 定义了 packer build 的逻辑. 这就是我们在 :ref:`prepare-packer-templates` 中提到的 jinja2 模板. 我建议你仔细看看这个文件中的注释, 了解对于不同 provision 的需求, 应该使用什么 packer 命令. 例如如果 provision 的逻辑非常复杂且有许多 Python 依赖, 这里的 ``complicated_script.sh`` 就是一个非常好的例子. 我建议你去 `example <https://github.com/MacHu-GWU/acore_ami-project/tree/main/packer_workspaces/example>`_ 目录下具体看看这个例子.

.. dropdown:: .pkr.hcl

    .. literalinclude:: ../../../packer_workspaces/example/templates/.pkr.hcl
       :language: hcl
       :linenos:

``.pkrvars.hcl``: packer variables 的值. packer build 的时候会从这里面读数据.

.. dropdown:: .pkrvars.hcl

    .. literalinclude:: ../../../packer_workspaces/example/templates/.pkrvars.hcl
       :language: hcl
       :linenos:

``.variables.pkr.hcl``: packer variables 的声明文件. 注意这里只是定义, 而不包含 value. (see https://developer.hashicorp.com/packer/guides/hcl/variables for more information)

.. dropdown:: .variables.pkr.hcl

    .. literalinclude:: ../../../packer_workspaces/example/templates/.variables.pkr.hcl
       :language: hcl
       :linenos:

``packer_build.py`` 这是一个 Python 脚本, 用来运行 packer build. **也是我们的核心脚本**. 这个脚本的主要流程是:

1. 读取 :class:`~acore_ami.workspace.WorkflowParam`
2. 读取 :class:`~acore_ami.workspace.StepParam`
3. 执行 packer build, 包括用 jinja2 render 最终的 packer template, 运行 ``packer validate`` 以及最终运行 ``packer build``, 这些逻辑被 :meth:`acore_ami.workspace.Workspace.run_packer_build_workflow` 方法封装在一起了.
4. 给 AMI 打上 aws tags, 便于管理.
5. 在 DynamoDB 中创建一条记录, 用来记录这个 AMI 的 metadata, 也方便以后进行查询和管理.

我建议你仔细 ``packer_build.py`` 源码中的注释来了解这个脚本的逻辑.

.. dropdown:: packer_build.py

    .. literalinclude:: ../../../packer_workspaces/example/packer_build.py
       :language: python
       :linenos:


Manage AMIs
------------------------------------------------------------------------------
AWS 官方有很多 AMI API 可以进行 list, get details 等操作. 但是灵活性还是远远不如用数据库来管理 metadata. 所以在这个项目中我们会用 DynamoDB 来管理 AMI 的 metadata, 使得我们可以更方便地操作 AMI.
