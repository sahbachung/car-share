import os.path
from shutil import rmtree

from base_type.controller import LocalController
from base_type.query import BaseQuery

class Builder(BaseQuery):

    @staticmethod
    def load_commands(fp) -> list:
        with open(fp, "r") as file:
            commands = []
            current = file.readline().strip()
            while current:
                while current[-1] != ";":
                    _ = current
                    current += file.readline().strip()
                    if _ == current:
                        break
                commands.append(current)
                current = file.readline().strip()
            return commands


class Controller(LocalController):

    def __init__(self, current_user, **kwargs):
        # TODO implement Agent database controller
        cv2args = kwargs.pop("cv2")
        s = kwargs.get("schema", "car-share/Agent/schema.sql")
        super().__init__(**kwargs)
        self.schema = s
        kwargs = cv2args
        self.face_dir = kwargs.get("faces")
        self.current_user = current_user
        self._engine_args = (kwargs["encodings"], kwargs["device_id"])
        if os.path.exists(kwargs["encodings"]):
            try:
                from Agent.facial_recognition import FaceDetectionEngine
                self.engine = FaceDetectionEngine(self, encodings=kwargs.get("encodings"), dev=kwargs.get("device_id", 0))
            except ImportError:
                print("Face detect compatibility not detected")
                self.engine = None

        else:
            self.engine = None

    def get_dir(self, username) -> str:
        # TODO get a dir to a saved face
        self.cu.execute(f"SELECT dir FROM user WHERE user LIKE {username}")
        resultset = self.cu.fetchall()
        if not resultset:
            return ""
        return self.face_dir + resultset[0][0]

    def gather_face(self, username):
        if not self.engine:
            from Agent.facial_recognition.facial_recognition import FaceDetectionEngine
            self.engine = FaceDetectionEngine(self, encodings=self._engine_args[0], dev=self._engine_args[1])
        path = self.face_dir + f"/{username}/"
        print(path)
        if os.path.exists(path):
            if input("Data exists! Retake photos? [Y/N]").upper() == "Y":
                rmtree(path)
            else:
                exit()
        if self.engine.save_photos(path):
            self.cu.execute(f"INSERT INTO user(username, password, dir) VALUES ('{username}'"
                            f", '{self.get_current_user_password()}', '{path}')")

    def login_with_face(self) -> tuple:
        username = self.engine.compare_face()
        self.cu.execute(f"SELECT password FROM user WHERE username LIKE '{username}'")
        password = self.cu.fetchall()
        if password:
            password = password[0][0]
        else:
            password = None
        return username, password

    def find_user_dir(self) -> str:
        self.cu.execute(f"SELECT dir FROM user WHERE username LIKE '{self.current_user}'")
        result_set = self.cu.fetchall()
        if not result_set:
            return ""
        return result_set[0][0]

    def get_current_user_password(self) -> str:
        self.cu.execute(f"SELECT password FROM user WHERE username LIKE '{self.current_user}'")

    def wipe_database(self):
        super().init_database(self.schema, db=self.db, qb=Builder)

