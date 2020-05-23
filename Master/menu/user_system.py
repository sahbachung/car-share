import re
import string
from getpass import getpass

from base_type.menu import BaseMenu


def validate_password(key) -> bool:
    print(key)
    special = False
    capital = False
    length = len(key) >= 8
    for char in key:
        if char in string.ascii_uppercase:
            capital = True
        if char in """ !"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~""":
            special = True
    print(special, capital, length)
    return special and capital and length


def parse_name(name) -> tuple:
    i = name.find(" ")
    if i <= 0:
        return tuple(name)
    return name[:i], name[i + 1:]


class UserMenu(BaseMenu):
    base_menu = "Choose an option:\n\t0: Quit\n\t1: Login\n\t2: Register\n\t3: Book Car"

    def __init__(self, controller, start=True):
        super().__init__(controller, start=start, commands=[
            self.quit,
            self.login,
            self.register,
            self.book_car])

    def login(self, username=None, password=None):
        if not username:
            username = input("Username: ")
        if not self.controller.query_username(username):
            print("User not found!")
            return
        password_hash = self.controller.hash_function(password)
        if not self.controller.verify_hash(username, password_hash):
            print("Incorrect details!")
        else:
            self.current_user = username

    def register(self) -> bool:
        print("Press Ctr+C to go back")
        username = ""
        password = ""
        password_hash = ""
        email = ""
        try:
            while True:
                if not username:
                    username = input("Username: ")
                    if len(username) < 6:
                        print("Username too short")
                        username = ""
                        continue
                    if not self._validate_username_free(username):
                        print("Username taken!")
                        username = ""
                        continue
                if not password:
                    password = getpass()
                    if not validate_password(password):
                        print(self.password_help)
                        password = ""
                        continue
                if password and not password_hash:
                    if getpass("Confirm: ") != password:
                        print("Passwords don't match")
                        password = ""
                        continue
                    password_hash = self.controller.hash_function(password)
                if not email:
                    email = input("Email: ")
                    if not re.findall(".*@.*\..*", email):
                        print("Invalid email")
                        email = ""
                        continue
                first_name = input("Enter full name: ")
                if first_name.find(" ") > 0:
                    first_name, last_name = parse_name(first_name)
                else:
                    last_name = ""
                if not self.controller.register_user(username, password_hash, first=first_name, last=last_name,
                                                     email=email):
                    raise Exception("Register Failed")
                return True
        except KeyboardInterrupt:
            return False

    def book_car(self, car_choice=None, date=None, time=None):
        if not self.current_user:
            return print("Log in to view and book cars")
        if car_choice is None:
            try:
                car_choice = int(input("Car id: "))
            except ValueError:
                print("Invalid input!")
                return self.book_car()
            if not self.controller.get_car(car_choice):
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
        self.controller.cal.add_event(self.current_user, car_choice, date + " " + time, duration)

    def _validate_username_free(self, name) -> bool:
        return not self.controller.query_username(name)


def main():
    menu = Menu(None)
    while menu.on:
        choice = menu.menu_choice()
        menu.commands[choice]()


if __name__ == "__main__":
    main()
