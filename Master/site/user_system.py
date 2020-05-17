from getpass import getpass
import hashlib


class Menu():

	def __init__(self):
		self.on = True
		self.commands = [
			self.quit,
			self.login,
			self.register,	
		]

	def menu_choice(self) -> int:
		print("Choose an option:\n" +
				"\t0: Quit\n" +
				"\t1: Login\n" +
				"\t2: Register\n" +
				"")
		try:
			i = int(input("Input choice (0-%d): " % len(self.commands)-1))
			if len(self.commands) <= i < 0: 
				raise ValueError
			return i
		except ValueError:
			print("Invalid option")
			return self.menu_choice()


	def login(self):
		uname = input("Username: ")
		passwd = hashlib.sha1(getpass().encode("utf-8"))


	def register(self):
		uname = input("Username: ")
		passwd = hashlib.sha1(getpass().encode("utf-8"))
		if passwd[32:]!=hashlib.sha1(getpass("Confirm Password: ").encode("utf-8")):
			return print("Passwords don't match")

	def quit(self):
		self.on = False


def main():
	menu = Menu()
	while menu.on:
		choice = menu.menu_choice()
		menu.commands[choice]()



if __name__ == "__main__":
	main()