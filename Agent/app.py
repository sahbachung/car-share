from Agent.controller import Controller
from Agent.menu.admin_system import AdminMenu
from Agent.menu.user_system import UserMenu


class Agent:

    def __init__(self, **kwargs):
        print(kwargs)
        self.program = kwargs["program"]
        self.controller = Controller(current_user=kwargs.get("user"), **kwargs["local_database"])
        self.config = kwargs
        self.menu = None

    def run(self, **kwargs):
        print(f"Initialized app as Agent\nRunning {self.program} program")
        self.controller.current_user = kwargs.get("username")
        if self.program == "user":
            self.menu = self.user()
        if self.program == "admin":
            self.menu = self.admin()
        if self.controller.current_user:
            self.controller.current_user = self.menu.login(username=self.controller.current_user, password=None)
        self.menu.start()

    def user(self):
        return UserMenu(self.controller, self.config["server"])

    def admin(self):
        return AdminMenu(self.controller, self.config["server"])
