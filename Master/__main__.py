import argparse
from getpass import getpass
from json import load

from menu.user_system import Menu as UserMenu
from menu.admin_system import Menu as AdminMenu
from controller import Controller

def main():
	parser = argparse.ArgumentParser(
			description="Allows admin access to the database, as well as a tool for clients to register/sign in and book cars"
		)
	prog = parser.add_argument_group("program")
	prog.add_argument("program", choices=["user", "admin"])
	args = parser.parse_args()
	with open("Master/login.json") as file:
		login = load(file)
	if args.program=="user":
		menu = UserMenu(Controller(**login, password=getpass(), db="DEBUG"))
	elif args.program=="admin":
		conn = Controller(**login, password=getpass(), db="DEBUG")


if __name__=="__main__":
	main()