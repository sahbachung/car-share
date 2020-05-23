from abc import ABC, abstractmethod

from mysql.connector import MySQLConnection
from mysql.connector.errors import ProgrammingError
from getpass import getpass
import hashlib

from base_type.query import BaseQuery


class BaseController(ABC):

    cu = None

    def hash_function(self, password=None, prompt="Password: ") -> str:
        """returns the hexadecimal digest for a password, call hash_password() with no kwargs to get user input"""
        if not password:
            password = getpass(prompt=prompt)
        return hashlib.sha1(password.encode("utf-8")).hexdigest()

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def __enter__(self):
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

    @abstractmethod
    def use(self, db):
        ...

    def set_cursor(self, cu):
        self.cu = cu

    def init_database(self, schema_loc, db="DEBUG", qb=BaseQuery):
        for q in qb.load_commands(schema_loc):
            if "{database}" in q:
                q = q.format(database=db)
            if db == "DEBUG":
                print(q[:q.find(" ")] + "...")
            self.cu.execute(q)


class LocalController(MySQLConnection, BaseController):

    def __init__(self, **kwargs):
        self.db = kwargs.get("database")
        if not self.db:
            self.db = "DEBUG"
        k = {
            "user": "root",
            "host": "localhost",
            "port": "3306",
            "password": ""}
        for key in k:
            if key in kwargs:
                continue
            kwargs[key] = k[key]
        if kwargs["port"]:
            super().__init__(
                host=kwargs.get("host"),
                port=kwargs.get("port"),
                user=kwargs.get("user"),
                password=kwargs.get("password"))
        else:
            super().__init__(
                host=kwargs.get("host"),
                user=kwargs.get("user"),
                password=kwargs.get("password"))
        self.autocommit = True
        self.cu = self.cursor()
        self.use(self.db)

    def __enter__(self):
        self.autocommit = False
        self.cu.execute(f"USE {self.db};")
        return self

    def __exit__(self, type, value, tb):
        if type(tb) == KeyboardInterrupt:
            self.cu.execute(f"COMMIT;")
        self.autocommit = True

    def use(self, db):
        try:
            self.cu.execute(f"USE %s" % db)
        except ProgrammingError:
            self.cu.execute(f"CREATE DATABASE %s" % db)
            self.use(db)
