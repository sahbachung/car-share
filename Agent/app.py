from Agent.menu.admin_system import AdminMenu
from Agent.menu.user_system import UserMenu
from Agent.controller import Controller


class Agent:

    def __init__(self, **kwargs):
        self.program = kwargs["program"]
        self.current_user = kwargs.get("username")
        self.controller = Controller(**kwargs["local_database"])
        self.config = kwargs

    def run(self):
        print(f"Agent {self.program}")
        if self.program == "user":
            self.user()
        if self.program == "admin":
            self.admin()

    def update_config(self, **kwargs):
        for key in kwargs:
            self.config[key] = kwargs[key]

    def user(self):
        menu = UserMenu(self.controller)
        if not menu.on:
            menu.login(username=self.current_user, password=self.config.get("password"))
        menu.start()

    def admin(self):
        menu = AdminMenu(self.controller)
        if not menu.on:
            menu.login(username=self.current_user, password=self.config.get("password"))
        menu.start()
