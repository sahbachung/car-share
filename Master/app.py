from Master.controller import Controller
from Master.menu.admin_system import AdminMenu
from Master.menu.user_system import UserMenu


class Master:

    def __init__(self, **kwargs):
        self.config = {
            "server": kwargs["server"],
            "master_database": kwargs["master_database"]
        }
        self.program = kwargs["program"]
        self.controller = Controller(**self.config["master_database"])

    def run(self, username=None, password=None):
        print(f"Initialized app as Master\nRunning {self.program} program")
        if self.program == "user":
            self.user()
        if self.program == "admin":
            self.admin(username=username, password=password)

    def user(self, **kwargs):
        menu = UserMenu(self.controller)

    def admin(self, username=None, password=None):
        menu = AdminMenu(self.controller, self.config["server"])
        menu.login(username=username, password=password)
        menu.start()
