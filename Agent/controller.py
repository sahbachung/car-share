import os.path
from shutil import rmtree

from base_type.controller import LocalController


class Controller(LocalController):

    def __init__(self, current_user, **kwargs):
        # TODO implement Agent database controller
        super().__init__(**kwargs)
        self.face_dir = kwargs.get("faces")
        self.current_user = current_user
        try:
            from Agent.facial_recognition import FaceDetectionEngine
            self.engine = FaceDetectionEngine(self, encodings=kwargs.get("encodings"), dev=kwargs.get("device_id", 0))
        except ImportError:
            print("Face detect compatibility not detected")
            self.engine = None

    def get_dir(self, username) -> str:
        # TODO get a dir to a saved face
        self.cu.execute(f"SELECT dir FROM user WHERE user LIKE {username}")
        resultset = self.cu.fetchall()
        if not resultset:
            return ""
        return self.face_dir + resultset[0][0]

    def gather_face(self, username, password):
        path = self.face_dir + f"/{username}/"
        if os.path.exists(path):
            if input("Data exists! Retake photos? [Y/N]").upper() == "Y":
                rmtree(path)
            else:
                exit()
        if self.engine.save_photos(path):
            self.cu.execute(f"INSERT INTO user(username, password, dir) VALUES ('{username}', '{password}', '{path}')")

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