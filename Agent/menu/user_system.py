from getpass import getpass

from base_type.menu import BaseMenu
from base_type.packet import Request, Response

from Agent.client import Client


class LoginMenu:

    def __init__(self, controller):
        self.controller = controller
        self.user, self.password = "", ""

    def login(self, e:bool = False) -> (str, str):
        commands = [
            exit,
            self.login_with_creds
        ]
        if e:
            commands.append(self.login_with_face)
        print(f"Choose an option [0-{len(commands)-1}]")
        print("\t0: Quit")
        print("\t1: Login with username and password")
        if e:
            print("\t2: Login with face")
        i = -1
        while i < 0 or i >= len(commands):
            try:
                i = int(input(f"Enter option: "))
            except ValueError:
                continue
            except KeyboardInterrupt:
                commands[0]()
        return commands[i]()

    def login_with_creds(self) -> (str, str):
        username = ""
        password = ""
        while not username:
            username = input("Username: ")
            if not username:
                continue
            key = getpass()
            password = self.controller.hash_function(password=key)
        self.user = username
        self.password = password
        return username, password

    def login_with_face(self) -> (str, str):
        username, password = self.controller.login_with_face()
        if not username:
            print("Failed to login with faces, logging with credentials")
            username, password = self.login_with_creds()
        self.user = username
        self.password = password
        return username, password


class UserMenu(BaseMenu):

    def __init__(self, controller, server_config):
        self.current_login = None
        super().__init__(controller, commands=[
            self.quit,
            self.unlock_car,
            self.return_car,
            self.add_face
        ], start=False)
        self.base_menu += "\n\t1: Unlock Car\n\t2: Return car\n\t3: Scan face"
        self.config = server_config

    def login(self, username=None, password=None, force=False) -> str:
        if username:
            password = self.controller.hash_function(getpass())
        else:
            self.current_login = LoginMenu(self.controller)
            username, password = self.current_login.login()
        with Client(self.config) as client:
            response = client.login(user=username, password=password)
        if response:
            return username
        else:
            print("Incorrect username or password")
            return ""

    def verify_user(self) -> bool:
        car_id = int(input("THIS VEHICLE'S ID: "))
        with Client(self.config) as client:
            response = Request.USER_VERIFY.send(client, user=self.controller.current_user, car_id=car_id)
        return bool(response)

    def unlock_car(self):
        if not self.verify_user():
            print("---UNAUTHORISED USER---")
        else:
            print("---SUCCESSFULLY UNLOCKED CAR---")

    def return_car(self):
        car_id = int(input("THIS VEHICLE'S ID: "))
        with Client(self.config) as client:
            response = Request.CAR_RETURN.send(client, user=self.controller.current_user, car_id=car_id)
        if response:
            print("---CAR SUCCESSFULLY RETURNED---")
            self.quit()
        elif response is Response.RETURN_ERROR:
            print("---COULD NOT RETURN CAR")
        else:
            print(response)

    def add_face(self):
        self.controller.gather_face(self.current_login.user)

    def quit(self):
        super().quit()

    def local_user(self, user) -> bool:
        return bool(self.controller.find_user_dir())

    def start(self):
        super().start()


