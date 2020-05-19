from abc import ABC, abstractmethod


class BaseMenu(ABC):

	def __init__(self, controller, start=True, commands=None):
		self.on = start
		self.controller = controller
		self.commands = commands
		self.current_user = None
		if self.on:
			self.start()

	def start(self):
		self.on = True
		try:
			while self.on:
				choice = self.menu_choice()
				self.commands[choice]()
		except KeyboardInterrupt:
			self.quit()

	def menu_choice(self, f=True) -> int:
		if self.current_user:
			print("Welcome {0}!".format(self.current_user))
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

	def quit(self):
		self.on = False

	@abstractmethod
	def login(self, username=None, password=None): ...