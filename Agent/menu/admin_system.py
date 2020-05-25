from Agent.client import Client
from base_type.menu import BaseMenu


class AdminMenu(BaseMenu):
    base_menu = "Choose an option:\n\t0: Quit\n\t1: Reinitialise DB"
    warning = "WARNING!\nRUNNING THIS COMMAND WILL COMPLETELY DESTROY THE DATABASE!\nAre you sure you want to continue"\
              "? (Y/N): "

    def __init__(self, controller, server_config):
        commands = [self.quit, self.reinit]
        super().__init__(controller, start=False, commands=commands)
        self.config = server_config

    def login(self, username=None, password=None):
        if not username:
            username = input("Username: ")
        if not password:
            password = self.controller.hash_function()
        with Client(self.config) as client:
            response = client.login(username, password)
            print(response)

    def reinit(self):
        if input(self.warning).upper() != "Y":
            return
        self.controller.init_database(schema_loc=self.controller._config["schema"])

    def start(self):
        if not self.controller.current_user:
            print("ERROR: NOT LOGGED IN")
            self.login()
            self.start()
        super().start()

