import argparse
from getpass import getpass
from json import load

from .menu.user_system import Menu as UserMenu
from .menu.admin_system import Menu as AdminMenu
from .controller import Controller

def main():
	parser = argparse.ArgumentParser(
			description="Allows admin access to the database, as well as a tool for clients to register/sign in and book cars"
		)
	prog = parser.add_argument_group("program")
	prog.add_argument("program", choices=["user", "admin"])
	parser.add_argument("-u", dest="username", type=str, default=None)
	parser.add_argument("-p", dest="password", type=str, default=None)
	args = parser.parse_args()
	with open("Master/login.json") as file:
		login = load(file)
	if args.program=="user":
		print(args.username)
		menu = UserMenu(Controller(**{"user":"root","host":"localhost","port":"3306","password":""}, db="DEBUG"), start=not bool(args.username))
		if not menu.on:
			menu.login(username=args.username, password=args.password)
			menu.start()
	elif args.program=="admin":
		menu = AdminMenu(Controller(**{"user":"root","host":"localhost","port":"3306","password":""}, db="DEBUG", start=not bool(args.username))
		if not menu.on:
			menu.login(username=args.username, password=args.password)
			menu.start()


if __name__=="__main__":
	main()