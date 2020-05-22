import argparse
import hashlib
import string
from getpass import getpass
import json
from enum import Enum

from Agent.app import Agent
from Master.app import Master


CONFIG_FILE = "config.json"
NO_PASSWORD = 'da39a3ee5e6b4b0d3255bfef95601890afd80709'


class Roles(Enum):

    Agent = "Agent"
    Master = "Master"
    NONE = "Default"

    def get_prog(self, **kwargs):
        program = kwargs["program"]
        username = kwargs.get("username")
        password = kwargs.get("password")
        server_config = kwargs["server"]
        master_database_config = kwargs["master_database"]
        local_database_config = kwargs["local_database"]
        if self == Roles.NONE:
            raise ValueError
        elif self == Roles.Agent:
            return Agent(**kwargs)
        elif self == Roles.Master:
            return Master(**kwargs)
        raise Exception


def get_kwargs(**kwargs) -> dict:
    if kwargs.get("username"):
        kwargs["username"] = kwargs["username"][0]
    return kwargs


def get_packet_header(packet_length, header_length=None) -> bytes:
    if not header_length:
        with open(CONFIG_FILE) as conf:
            header_length = json.load(conf)["packet_header_length"]
    return bytes(f"{packet_length:<{header_length}}", encoding="utf-8")


def hash_password(password=None) -> str:
    """returns the hexadecimal digest for a password, call hash_password() with no kwargs to get user input"""
    if not password:
        password = getpass()
    return hashlib.sha1(password.encode("utf-8")).hexdigest()


def validate_password(key) -> bool:
    special = False
    capital = False
    length = len(key) > 8
    for char in key:
        if char in string.ascii_uppercase:
            capital = True
        if char in """ !"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~""":
            special = True
    return special and capital and length


def parse_name(name) -> tuple:
    i = name.find(" ")
    if i <= 0:
        return tuple(name)
    return name[:i], name[i+1:]


def parse_args(desc=""):
    parser = argparse.ArgumentParser(description=desc)
    program = parser.add_argument_group("program")
    program.add_argument("program", choices=["user", "admin"])
    parser.add_argument("-u", dest="username", type=str, default=None)
    parser.add_argument("-p", dest="password", type=str, default=None)
    args = parser.parse_args()
    return args


