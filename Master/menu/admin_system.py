from getpass import getpass
import hashlib

from .menu import BaseMenu


class Menu(BaseMenu):

	base_menu = "Choose an option:\n\t0: Quit\n\t1: Reinitialise DB"
	warning = "WARNING!\nRUNNING THIS COMMAND WILL COMPLETLY DESTROY THE DATABASE!\nAre you sure you want to continue? (Y/N): "

	def __init__(self, controller, start=True):
		super().__init__(controller, start=start, commands=[
			self.quit,
			self.reinit])

	def menu_choice(self, f=True) -> int:
		if not self.current_user:
			raise CredError("Not logged in as Admin")
		if f:
			print(self.base_menu)
		try:
			i = int(input("Input choice (0-%d): " % (int(len(self.commands))-1)))
			if len(self.commands) <= i or i < 0: 
				raise ValueError
			return i
		except ValueError:
			print("Invalid option")
			return self.menu_choice(False)

	def reinit(self):
		if input(self.warning).upper()!="Y":
			return
		self.controller.init_database("Master/schema.sql")

	def login(self, username=None, password=None):
		if not username:
			username = input("Input username: ")
		if not self.controller.query_username(username):
			print("User not found!")
			return
		if not password:
			passhash = hashlib.sha1(getpass().encode("utf-8")).hexdigest()
		else:
			passhash = hashlib.sha1(password.encode("utf-8")).hexdigest()
		if not self.controller.verify_hash(username, passhash):
			print("Incorrect details!")
		elif not self.controller.get_user_details(username)[3] > 0:
			raise CredError("Not an Admin account")
		else:
			self.current_user = username


class CredError(Exception):
	pass