import argparse
import json
import os
from getpass import getpass


import build


def main():
    parser = argparse.ArgumentParser(description="Control center for the car-share app")
    program = parser.add_argument_group("program")
    program.add_argument(
        "program",
        type=str, choices=["user", "admin"],
        help="program to run")
    program.add_argument(
        "-u", "--username", dest="user",
        type=str,
        help="use provided username", required=False)
    program.add_argument(
        "-p", dest="use_password",
        default=False, action="store_true",
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
    program.add_argument(
        "-s", "--use-ssl",
        dest="ssl", default=False,
        action="store_true",
        help="provide the mysql server ssl credentials")
    program.add_argument(
        "-a", "--use-service-account",
        dest="sa", default=False,
        action="store_true",
        help="use service"
    )
    args = parser.parse_args()
    with open(args.config) as conf:
        config = json.load(conf)
    if args.use_password:
        password = getpass()
    else:
        password = None
    print(args.role)
    if args.role == "Default":
        args.role = os.getenv("CAR_SHARE_ROLE", "Default")
    print(config)
    prog = build.build(args.role, program=args.program, **config)
    prog.run(username=args.user, password=password)


if __name__ == "__main__":
    main()
