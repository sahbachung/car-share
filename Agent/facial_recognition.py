import os

import cv2


def get_camera(device_id):
    c = cv2.VideoCapture(device_id)
    c.set(3, 640)
    c.set(4, 480)
    return c


class FaceDetectionEngine:

    def __init__(self, controller, dev=0):
        # TODO implement FaceDetectionEngine
        self.controller = controller
        self.camera = get_camera(dev)
        self.face_detector = cv2.CascadeClassifier("Agent/haarcascade_frontalface_default.xml")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def detect_face(self):
        # TODO implement me
        pass

    def compare_face(self) -> bool:
        # TODO implement me
        return bool(self)

    def save_photos(self, folder, count=10):
        img_counter = 0
        if not os.path.exists(folder):
            os.makedirs(folder)
        while img_counter <= count:
            key = input("Press q to quit or ENTER to continue: ")
            if key == "q":
                break
            ret, frame = self.camera.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
            if len(faces) == 0:
                print("No face detected, please try again")
                continue
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                img_name = "{}/{:04}.jpg".format(folder, img_counter)
                cv2.imwrite(img_name, frame[y: y + h, x: x + w])
                print("{} written!".format(img_name))
                img_counter += 1
