# -*- coding: utf-8 -*-

from acore_ami import api


def test():
    _ = api


if __name__ == "__main__":
    from acore_ami.tests import run_cov_test

    run_cov_test(__file__, "acore_ami.api", preview=False)
