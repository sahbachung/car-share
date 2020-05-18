from getpass import getpass
from controller import Controller
import hashlib
import string
import re


class Menu():

	base_menu = "Choose an option:\n\t0: Quit\n\t1: Login\n\t2: Register"
	password_help = "Password requirements:\n\t- 8+ characters\n\t- 1+ capital letters\n\t- 1+ special characters"

	def __init__(self, controller, start=True):
		self.on = start
		self.cu = controller.cu
		self.connection = controller
		self.commands = [
			self.quit,
			self.login,
			self.register,	
		]
		self.current_user = None
		if start:
			self.start()

	def start(self):
		self.on = True
		while self.on:
			choice = self.menu_choice()
			self.commands[choice]()

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

	def login(self):
		uname = input("Username: ")
		if not self.connection.query_username(uname):
			print("User not found!")
			return
		passhash = hashlib.sha1(getpass().encode("utf-8")).hexdigest()
		if not self.connection.verify_hash(uname, passhash):
			print("Incorrect details!")
			return 
		self.connection.update_lastlogin(uname)
		self.current_user = uname


	def register(self) -> bool:
		print("Press Ctr+C to go back")
		uname = ""
		password = ""
		email = ""
		try:
			while True:
				if not uname:
					uname = input("Username: ")
					if len(uname) < 6:
						print("Username too short")
						uname = ""
						continue
					if not self._validate_username_free(uname):
						print("Username taken!")
						uname =""
						continue
				if not password:
					password = getpass()
					if password!=getpass("Confirm: "):
						print("Passwords don't match")
						password = ""
						continue
					if not self._validate_password(password):
						print(self.password_help)
						password = ""
						continue
					passhash = self.hash_password(password).hexdigest()
				if not email:
					email = input("Email(leave blank for none): ")
					if email!="" and not re.findall(".*@.*\..*", email):
						print("Invalid email")
						email = ""
						continue
				firstname = input("Enter full name: ")
				if firstname.find(" ") > 0:
					firstname, lastname = self._parse_name(firstname)
				if not self.connection.register_user(uname, passhash, first=firstname, last=lastname, email=email):
					raise Exception("Register Failed")
				self.connection.update_lastlogin(uname)
				self.current_user = uname
				return
		except KeyboardInterrupt:
			return

	def quit(self):
		self.on = False

	def hash_password(self, password):
		return hashlib.sha1(password.encode("utf-8"))
		
	def _validate_username_free(self, name) -> bool:
		return not self.connection.query_username(name)

	def _validate_password(self, key) -> bool:
		spcl = False
		cap = False
		l = len(key)
		for c in key:
			if c in string.ascii_uppercase: cap = True
			if c in """ !"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~""": spcl = True
		return spcl and cap and l

	def _parse_name(self, name) -> tuple:
		i = name.find(" ")
		if i <= 0: 
			return tuple(name)
		return name[:i], name[i+1:]

def main():
	menu = Menu()
	while menu.on:
		choice = menu.menu_choice()
		menu.commands[choice]()



if __name__ == "__main__":
	main()