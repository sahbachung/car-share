from getpass import getpass
from .menu import BaseMenu

class Menu(BaseMenu):

	base_menu = "Choose an option:\n\t0: Quit\n\t1: Reinitialise DB"

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
		warning = """WARNING!
		RUNNING THIS COMMAND WILL COMPLETLY DESTROY THE DATABASE!
		Are you sure you want to continue? (Y/N): """
		if input(warning).upper()!="Y":
			return
		self.controller.init_databse("Master/schema.sql")

	def login(self):...

class CredError(Exception):
	pass