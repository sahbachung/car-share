from getpass import getpass
import hashlib

from .. import Server
from base_type.menu import BaseMenu


class AdminMenu(BaseMenu):

	base_menu = "Choose an option:\n\t0: Quit\n\t1: Reinitialise DB"
	warning = "WARNING!\nRUNNING THIS COMMAND WILL COMPLETELY DESTROY THE DATABASE!\nAre you sure you want to continue? " \
		"(Y/N): "

	def __init__(self, controller, start=True):
		super().__init__(controller, start=start, commands=[
			self.quit,
			self.reinit,
			self.start_server
		])

	def menu_choice(self, f=True) -> int:
		if not self.current_user:
			raise CredError("Not logged in as Admin")
		return super().menu_choice()

	def reinit(self):
		if input(self.warning).upper() != "Y":
			return
		self.controller.init_database("Master/schema.sql")

	def login(self, username=None, password=None):
		if not username:
			username = input("Input username: ")
		if not self.controller.query_username(username):
			print("User not found!")
			return
		if not password:
			password_hash = self.hash_password()
		else:
			password_hash = self.hash_password(password)
		if not self.controller.verify_hash(username, password_hash):
			print("Incorrect details!")
		elif not self.controller.get_user_details(username)[3] > 0:
			raise CredError("Not an Admin account")
		else:
			self.current_user = username

	def start_server(self):
		with Server(self.controller) as server:
			print("Press Ctrl+C to close the server")
			server.listen()


class CredError(Exception):
	pass
