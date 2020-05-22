from getpass import getpass

from base_type.menu import BaseMenu


class UserMenu(BaseMenu):

    base_menu = "Choose an option:\n\t0: {login}\n\t1: Unlock Car\n\t2: Return car"

    def __init__(self, controller):
        super().__init__(controller, commands=[
            self.quit,
            self.unlock_car,
            self.return_car
        ])

    def login(self, username=None, password=None) -> str:
        if username:
            password = self.hash_password(getpass())
        else:
            print("Input verification method:")
            print("\t0: Quit")
            print("\t1: Enter credentials")
            print("\t2: Detect Face")

        return ""

    def unlock_car(self):  # TODO implement me
        ...

    def return_car(self):  # TODO implement me
        ...
