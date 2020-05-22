from Master.menu.admin_system import AdminMenu
from Master.menu.user_system import UserMenu
from Master.controller import Controller


class Master:

    def __init__(self, **kwargs):
        self.program = kwargs["program"]
        self.current_user = kwargs.get("username")
        self.controller = Controller(**kwargs["master_database"])
        self.config = kwargs

    def run(self):
        print(f"Master {self.program}\nkwargs={self.config}")
        if self.program == "user":
            self.user()
        if self.program == "admin":
            self.admin()

    def update_config(self, **kwargs):
        for key in kwargs:
            self.config[key] = kwargs[key]

    def user(self):
        menu = UserMenu(self.controller, start=bool(self.config.get("username")))
        if not menu.on:
            menu.login(username=self.current_user, password=self.config.get("password"))
        menu.start()

    def admin(self):
        menu = AdminMenu(self.controller, start=False)
        if not menu.on:
            menu.login(username=self.current_user, password=self.config.get("password"))
        menu.start()
