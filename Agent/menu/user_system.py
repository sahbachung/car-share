from getpass import getpass

from base_type.menu import BaseMenu
from base_type.packet import Request, Response

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

    def login(self, username=None, password=None, force=False):
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
            response = client.login(user=username, password=password)
        if response:
            self.controller.current_user = username
        else:
            print("Incorrect username or password")

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
        car_id = int(input("THIS VEHICLE'S ID: "))
        with Client(self.config) as client:
            response = Request.USER_VERIFY.send(client, user=self.current_user, car_id=car_id)
        return bool(response)

    def unlock_car(self):
        if not self.verify_user():
            print("---UNAUTHORISED USER---")
        else:
            print("---SUCCESSFULLY UNLOCKED CAR---")

    def return_car(self):
        car_id = int(input("THIS VEHICLE'S ID: "))
        with Client(self.config) as client:
            response = Request.CAR_RETURN.send(client, user=self.current_user, car_id=car_id)
        if response:
            print("---CAR SUCCESSFULLY RETURNED---")
            self.quit()
        elif response is Response.RETURN_ERROR:
            print("---COULD NOT RETURN CAR")
        else:
            print(response)