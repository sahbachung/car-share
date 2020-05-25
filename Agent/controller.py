import os.path
from shutil import rmtree

from base_type.controller import LocalController

from Agent.facial_recognition import FaceDetectionEngine


class Controller(LocalController):
    face_dir = "car-share/Agent/faces/"

    def __init__(self, current_user, **kwargs):
        # TODO implement Agent database controller
        super().__init__(**kwargs)
        self.current_user = current_user
        self.engine = FaceDetectionEngine(self)

    def get_dir(self, username) -> str:
        # TODO get a dir to a saved face
        self.cu.execute(f"SELECT dir FROM user WHERE user LIKE {username}")
        resultset = self.cu.fetchall()
        if not resultset:
            return ""
        return self.face_dir + resultset[0][0]

    def gather_face(self, username):
        path = self.face_dir + f"/{username}/"
        if os.path.exists(path):
            if input("Data exists! Retake photos? [Y/N]").upper() == "Y":
                rmtree(path)
            else:
                exit()
