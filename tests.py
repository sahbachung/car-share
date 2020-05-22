import unittest

import json

from Master.app import Master
from Agent.app import Agent

from utils import Roles, get_kwargs, NO_PASSWORD, CONFIG_FILE

GLOBAL_CONFIG = None
try:
    with open(CONFIG_FILE, "r") as conf:
        GLOBAL_CONFIG = json.load(conf)
except FileNotFoundError:
    pass


class BaseMenuTest:

    global GLOBAL_CONFIG

    def get_prog(self, role, program, **kwargs):
        return Roles(role).get_prog(program=program, **kwargs)


class TestMenu(unittest.TestCase, BaseMenuTest):
    def test_master_user(self):
        prog = self.get_prog(
            "Master", "user",
            **get_kwargs(username="root_no_password", password=NO_PASSWORD),
            **GLOBAL_CONFIG
        )
        self.assertTrue(type(prog) == Master)


if __name__ == '__main__':

    unittest.main()
