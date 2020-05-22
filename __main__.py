from Master.app import Master
from Agent.app import Agent

import argparse
import os
from sys import argv
from enum import Enum
import json

from utils import hash_password, NO_PASSWORD, Roles, get_kwargs


def main():
    # TODO !!!RE IMPLEMENT config.json PLEASE!!! #
    parser = argparse.ArgumentParser(description="Control center for the car-share app")
    program = parser.add_argument_group("program")
    program.add_argument(
        "program",
        type=str, choices=["user", "admin"],
        help="program to run")
    program.add_argument(
        "-u", "--username", dest="user",
        type=str, nargs=1,
        help="use provided username", required=False)
    program.add_argument(
        "-p", dest="use_password",
        default=True, action="store_true",
        help="use a password to login")
    program.add_argument(
        "-R", dest="role",
        type=str, default="Default",
        choices=["Default", "Master", "Agent"],
        help="override the environment variable 'CAR_SHARE_ROLE'")
    program.add_argument(
        "-C", dest="config",
        type=str, default="car-share/config.json",
        help="configuration file for the app; default='car-share/config.json'")
    args = parser.parse_args()
    with open(args.config) as conf:
        config = json.load(conf)
    password = None
    if args.program == "user":
        args.user = input("Username: ")
    if not args.user:
        if args.use_password:
            password = hash_password()
        else:
            password = NO_PASSWORD
    if args.role == "Default":
        args.role = os.getenv("CAR_SHARE_ROLE")
    kwargs = get_kwargs(program=args.program, username=args.user, password=password)
    prog = Roles(args.role).get_prog(**kwargs, **config)
    prog.run(**config)


if __name__ == "__main__":
    main()
