from Agent.controller import Controller
from Agent.menu.admin_system import AdminMenu
from Agent.menu.user_system import UserMenu

from base_type.app import App


class Agent(App):

    def __init__(self, **kwargs):
        super().__init__()
        self.program = kwargs["program"]
        self.controller = Controller(None, **kwargs["local_database"])
        self.config = kwargs
        self.menu = None

    def run(self, **kwargs):
        print(f"Initialized app as Agent\nRunning {self.program} program")
        self.controller.current_user = kwargs.get("username")
        if self.program == "user":
            self.menu = UserMenu(self.controller, self.config["server"])
        if self.program == "admin":
            self.menu = AdminMenu(self.controller, self.config["server"])
        while not self.controller.current_user:
            self.controller.current_user = self.menu.login(username=self.controller.current_user, password=None)
        self.menu.start()
