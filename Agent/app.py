from Agent.controller import Controller
from Agent.menu.admin_system import AdminMenu
from Agent.menu.user_system import UserMenu


class Agent:

    def __init__(self, server_config, **kwargs):
        self.program = kwargs["program"]
        self.current_user = kwargs.get("username")
        self.controller = Controller(**kwargs["local_database"])
        self.config = {
            "server": server_config,
            **kwargs
        }

    def run(self, **kwargs):
        print(f"Initialized app as Agent\nRunning {self.program} program")
        if self.program == "user":
            self.user()
        if self.program == "admin":
            self.admin()

    def user(self):
        menu = UserMenu(self.controller, self.config["server"])
        if self.current_user:
            menu.login(username=self.current_user, password=None)
        else:
            menu.login()

    def admin(self):
        menu = AdminMenu(self.controller)
        if self.current_user:
            menu.login(username=self.current_user, password=None)
        else:
            menu.login()
