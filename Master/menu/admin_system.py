from Master.server import Server
from base_type.menu import BaseMenu
from Master.menu.user_system import UserMenu

from getpass import getpass


class AdminMenu(BaseMenu):
    base_menu = """Choose an option:
    0: Quit
    1: Reinitialise DB
    2: Start Server
    3: Register new user
    4: Book Car for user"""
    warning = "WARNING!\nRUNNING THIS COMMAND WILL COMPLETELY DESTROY THE DATABASE!\n" \
              "Are you sure you want to continue? (Y/N): "

    def __init__(self, controller, server_config):
        super().__init__(controller, commands=[
            self.quit,
            self.reinit,
            self.start_server,
            self.register,
            self.show_bookings
        ], start=False)
        self._server_config = server_config

    def reinit(self):
        if not self.current_user:
            self.login()
        if input(self.warning).upper() != "Y":
            return
        self.controller.init_database("car-share/Master/schema.sql")

    def login(self, username=None, password=None):
        if not self.controller.get_user_details(username):
            exit("USER NOT FOUND")
        elif not username:
            username = input("Input username: ")
            if not self.controller.query_username(username):
                username = None
            else:
                self.current_user = username
        if password is None:
            password_hash = self.controller.hash_function()
        else:
            password_hash = self.controller.hash_function(password=password)
        if not self.controller.verify_hash(username, password_hash) or self.controller.get_user_details(username)[1] != username:
            print("Incorrect details!")
            self.login(username=username, password=getpass())
        elif not self.controller.get_user_details(username)[3] > 0:
            raise CredError("Not an Admin account")
        else:
            self.current_user = username
        if self.current_user:
            self.controller.login(username, password)
            return
        else:
            self.login(username=username, password=getpass())

    def start_server(self):
        with Server(self.controller, self._server_config) as server:
            print("Press Ctrl+C to close the server")
            try:
                server.listen()
            except KeyboardInterrupt:
                return

    def register(self):
        UserMenu.register(self)

    def show_bookings(self):
        pass

    def _validate_username_free(self, name) -> bool:
        return not self.controller.query_username(name)


class CredError(Exception):
    pass
