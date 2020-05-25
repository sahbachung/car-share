from abc import ABC, abstractmethod


class BaseMenu(ABC):

    base_menu = "Choose an option:\n\t0: Quit"
    password_help = "Password requirements:\n\t- 8+ characters\n\t- 1+ capital letters\n\t- 1+ special characters"

    def __init__(self, controller, start=True, commands=None):
        self.on = start
        self.controller = controller
        self.commands = commands if commands else []
        self.current_user = None
        if self.on:
            self.start()

    def start(self):
        self.on = True
        try:
            while self.on:
                choice = self.menu_choice()
                self.commands[choice]()
        except KeyboardInterrupt:
            self.quit()

    def menu_choice(self, f=True) -> int:
        if self.current_user and f:
            print("Welcome {0}!".format(self.current_user))
        if f:
            print(self.base_menu)
        try:
            i = int(input(f"Input choice [0-{(len(self.commands)-1)}]: "))
        except ValueError:
            print(f"Please enter an number [0-{len(self.commands)-1}]: ")
            return self.menu_choice(False)
        else:
            if len(self.commands) <= i or i < 0:
                print("Invalid option")
                return self.menu_choice(False)
        if not i:
            exit(i)
        return i

    def quit(self):
        self.on = False
        self.current_user = None

    def add_command(self, label, command, menu="base_menu"):
        self.commands.append(command)
        setattr(self, menu, getattr(self, menu) + "\n" + label)

    @abstractmethod
    def login(self, username=None, password=None):
        ...
