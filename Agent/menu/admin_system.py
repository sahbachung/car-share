from base_type.menu import BaseMenu


class AdminMenu(BaseMenu):
    base_menu = "Choose an option:\n\t0: Quit\n\t1: Reinitialise DB"
    warning = "WARNING!\nRUNNING THIS COMMAND WILL COMPLETELY DESTROY THE DATABASE!\nAre you sure you want to continue? " \
              "(Y/N): "

    def __init__(self, controller):
        super().__init__(controller, commands=[
            self.quit,
            self.reinit
        ])

    def login(self, username=None, password=None):
        if not username:
            username = input("Username: ")
        if not password:
            password = self.controller.hash_function()

    def reinit(self):
        if input(self.warning).upper() != "Y":
            return
        self.controller.init_database("car-share/Agent/schema.sql")
