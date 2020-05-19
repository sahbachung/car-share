from getpass import getpass
from ..controller import Controller
import hashlib
import string
import re

from .menu import BaseMenu 

class Menu(BaseMenu):

	base_menu = "Choose an option:\n\t0: Quit\n\t1: Login\n\t2: Register\n\t3: Book Car"
	password_help = "Password requirements:\n\t- 8+ characters\n\t- 1+ capital letters\n\t- 1+ special characters"

	def __init__(self, controller, start=True):
		super().__init__(controller, start=start, commands=[
			self.quit, 
			self.login, 
			self.register, 
			self.book_car])
		

	def login(self, username=None, password=None):
		if username:
			uname = username
		else:
			uname = input("Username: ")
		if not self.connection.query_username(uname):
			print("User not found!")
			return
		if not password:
			passhash = hashlib.sha1(getpass().encode("utf-8")).hexdigest()
		else:
			passhash = hashlib.sha1(password.encode("utf-8")).hexdigest()
		if not self.connection.verify_hash(uname, passhash):
			print("Incorrect details!")
		else:
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
					email = input("Email: ")
					if not re.findall(".*@.*\..*", email):
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

	def book_car(self, car_choice=None, date=None, time=None):
		if not self.current_user:
			return print("Log in to view and book cars")
		if car_choice is None:
			try:
				car_choice = int(input("Car id: "))
			except ValueError:
				print("Invalid input!")
				return self.book_car()
			if not self.connection.get_car(car_choice):
				return print("Car id not found!")
		if date is None:
			print("Please enter the date of the booking in the form:\n\n\tYYYY/MM/DD\n")
			date = input("Enter date (YYYYY/MM/DD): ")
			if not re.search("[0-9]{4}/[0-9]{2}/[0-9]{2}", date):
				print("Invalid date format")
				return self.book_car(car_choice=car_choice)
			else:
				date = "".join(date.split("/"))
		if time is None:
			print("Please enter time in the form:\n\n\tHH:MM:SS AM/PM\n")
			time = input("Enter time (HH:MM:SS AM/PM): ")
			if not re.search("[0-9]{2}:[0-9]{2}:[0-9]{2} [AP]M", time):
				if not re.search("[0-9]{2}:[0-9]{2} [AP]M", time):
					print("Invalid time format!")
					return self.book_car(car_choice=car_choice, date=date)
				time = time[:5] + ":00" + time[5:]
		try:
			duration = int(input("Enter duration in days: "))
		except ValueError:
			print("Invalid input!")
			return self.book_car(car_choice=car_choice, date=date, time=time)
		if duration <= 0:
			print("Duration must be > 0")
			return self.book_car(car_choice=car_choice, date=date, time=time)
		self.connection.cal.add_event(self.current_user, car_choice, date+" "+time, duration)

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