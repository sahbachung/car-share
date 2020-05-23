from base_type.controller import LocalController

from Agent.facial_recognition import FaceDetectionEngine


class Controller(LocalController):
    face_dir = "Agent/faces/"

    def __init__(self, **kwargs):
        # TODO implement Agent database controller
        super().__init__(**kwargs)

    def get_face(self, username) -> str:
        # TODO get a dir to a saved face
        face = ""
        return self.face_dir + face
