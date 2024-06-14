Setup Local Python Development Environment
==============================================================================
该项目使用 `pyproject_ops <https://github.com/MacHu-GWU/pyproject_ops-project>`_ 来管理 Python 环境, 安装依赖等. 依次使用下列命令既可创建虚拟环境以及安装依赖:

.. code-block:: bash

    # 创建虚拟环境以及安装依赖
    pyops venv-create
    pyops install-all

    # 当依赖发生变更时输入下列命令重新 resolve 并安装依赖
    pyops poetry-lock
    pyops install-all

该项目的 python 库依赖的原始定义是在 `pyproject.toml <https://github.com/MacHu-GWU/acore_ami-project/blob/main/pyproject.toml>`_ 文件中, 而 ``requirements.txt`` 文件是由 `poetry <https://python-poetry.org/>`_ 自动生成的.

.. dropdown:: pyproject.toml

    .. literalinclude:: ../../../pyproject.toml
       :language: toml
       :linenos:

本项目更新于 2024-06-04, 根据 `python end of life status <https://devguide.python.org/versions/>`_ Python3.11 还有接近 3 年的生命周期, 并且已经经过 2 年的迭代变得比较成熟了, 而且我们项目的库目前没有发现不支持 3.11 的, 所以这个项目以及 AMI 中我们使用 Python3.11 作为默认的 Python 版本.
