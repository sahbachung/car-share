import argparse
import hashlib
from enum import Enum
from getpass import getpass

from Agent.app import Agent
from Master.app import Master

CONFIG_FILE = "car-share/config.json"

NO_PASSWORD = 'da39a3ee5e6b4b0d3255bfef95601890afd80709'  # sha1 hex digest of an empty string=''


class Roles(Enum):
    Agent = Agent
    Master = Master
    Default = None

    def build(self, **kwargs):
        program = kwargs["program"]
        server_config = kwargs["server"]
        master_database_config = kwargs["master_database"]
        local_database_config = kwargs["local_database"]
        return self.build_role([program, server_config, master_database_config, local_database_config])

    def build_role(self, args) -> Master or Agent:
        if self is Roles.Default:
            raise TypeError("Cannot build from role 'Default'")
        args, kwargs = self.get_params(*args)
        return self.value(*args, **kwargs)

    def get_params(self, *args) -> tuple:
        params = [[args[1]], {"program": args[0]}]
        if self is Roles.Agent:
            params[1]["local_database"] = args[3]
        elif self is Roles.Master:
            params[1]["master_database"] = args[2]
        return tuple(params)


def get_kwargs(**kwargs) -> dict:
    return kwargs


def hash_password(password=None, prompt="Password: ") -> str:
    """returns the hexadecimal digest for a password, call hash_password() with no kwargs to get user input"""
    if not password:
        password = getpass(prompt=prompt)
    return hashlib.sha1(password.encode("utf-8")).hexdigest()


def parse_name(name) -> tuple:
    i = name.find(" ")
    if i <= 0:
        return tuple(name)
    return name[:i], name[i + 1:]


def parse_args(desc=""):
    parser = argparse.ArgumentParser(description=desc)
    program = parser.add_argument_group("program")
    program.add_argument("program", choices=["user", "admin"])
    parser.add_argument("-u", dest="username", type=str, default=None)
    parser.add_argument("-p", dest="password", type=str, default=None)
    args = parser.parse_args()
    return args
