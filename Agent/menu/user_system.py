from getpass import getpass

from base_type.menu import BaseMenu
from base_type.packet import Request

from Agent.client import Client


class UserMenu(BaseMenu):

    def __init__(self, controller, server_config):
        super().__init__(controller, commands=[
            self.quit,
            self.unlock_car,
            self.return_car
        ], start=False)
        self.base_menu += "\n\t1: Unlock Car\n\t2: Return car"
        self.config = server_config

    def login(self, username=None, password=None):
        if username:
            password = self.controller.hash_function(getpass())
        else:
            print("How will you verify?")
            print("\t0: Quit")
            print("\t1: Enter credentials")
            print("\t2: Detect Face")
            i = -1
            while 0 > i or i > 2:
                try:
                    i = int(input("Input user verification method [0-2]: "))
                except ValueError:
                    continue
            if not i:
                exit(i)
            elif i == 1:
                username, password = self.in_login()
        with Client(self.config) as client:
            client.login(user=username, password=password)

    def in_login(self) -> tuple:
        username = ""
        password = ""
        while not username:
            username = input("Username: ")
            if not username:
                continue
            key = getpass()
            password = self.controller.hash_function(password=key)
        return username, password

    def verify_user(self) -> bool:
        with Client(self.config) as client:
            Request.USER_VERIFY.send(client, user=self.current_user)
        return False

    def unlock_car(self):  # TODO implement me
        if not self.verify_user():
            print("UNAUTHORISED USER")

    def return_car(self):  # TODO implement me
        ...
