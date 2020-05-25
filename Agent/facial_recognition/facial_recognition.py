import os
import pickle

import cv2
import imutils
from imutils import paths
from imutils.video import VideoStream
import time

try:
    import face_recognition
except ImportError:
    from unittest.mock import Mock as face_recognition

# import numpy as np
# import cv2
# faceCascade = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')
# cap = cv2.VideoCapture(0)
# cap.set(3,640) # set Width
# cap.set(4,480) # set Height
# while True:
#     ret, img = cap.read()
#     img = cv2.flip(img, -1)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     faces = faceCascade.detectMultiScale(
#         gray,
#         scaleFactor=1.2,
#         minNeighbors=5,
#         minSize=(20, 20)
#     )
#     for (x,y,w,h) in faces:
#         cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
#         roi_gray = gray[y:y+h, x:x+w]
#         roi_color = img[y:y+h, x:x+w]
#     cv2.imshow('video',img)
#     k = cv2.waitKey(30) & 0xff
#     if k == 27: # press 'ESC' to quit
#         break
# cap.release()
# cv2.destroyAllWindows()


class Camera(cv2.VideoCapture):

    def __init__(self, device_id):
        super().__init__(device_id)

    def __del__(self):
        self.release()


def get_camera(device_id, Type: type = Camera):
    if device_id is None:
        raise ValueError
    c = Type(device_id)
    c.set(3, 640)
    c.set(4, 480)
    return c


class FaceDetectionEngine:

    def __init__(self, controller, encodings="car-share/Agent/facial_recognition/encodings.pickle", dev=0):
        # TODO implement FaceDetectionEngine
        self.dev = dev
        self.controller = controller
        self.classifier = cv2.CascadeClassifier()
        self.encodings = encodings
        if not self.classifier.load("car-share/Agent/haarcascade_frontalface_default.xml"):
            raise RuntimeError("Couldn't load 'car-share/Agent/haarcascade_frontalface_default.xml")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def detect_face(self, frame) -> list:
        # TODO implement me
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.classifier.detectMultiScale(gray, 1.3, 5)

    def get_faces(self) -> tuple:
        faces = []
        frame = None
        while not faces:
            ret = False
            while not ret:
                try:
                    camera = get_camera(self.dev)
                except ValueError:
                    self.set_dev()
                    return self.get_faces()
                ret, frame = camera.read()
            faces = self.detect_face(frame)
        return faces, frame

    def encode_face(self, path):
        known_encodings = []
        known_names = []
        for i, image_path in enumerate(list(paths.list_images(path))):
            if image_path[-4:] in [".jpg", "jpeg"]:
                image = cv2.imread(image_path)
            else:
                continue
            name = os.path.basename(image_path[-1])
            rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)
            for encoding in encodings:
                known_encodings.append(encoding)
                known_names.append(name)

    def serialize(self, enc, names):
        print("Serializing encodings...")
        with open(self.encodings, "wb") as f:
            f.write(pickle.dumps({"encodings": enc, "names": names}))

    def compare_face(self, t=30) -> str:
        # TODO implement me
        with open(self.encodings, "rb") as f:
            data = pickle.loads(f.read())
        vs = get_camera(self.dev, VideoStream).start()
        start = time.time()
        while True:
            if time.time()-start >= t:
                return ""
            frame = vs.read()
            time.sleep(2)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = imutils.resize(rgb, width=240)

            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)
            name = self.match_encoding(data, encodings)
            if not name:
                continue
            return name

    def match_encoding(self, data, encodings) -> str:
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            if True in matches:
                matchedIndexes = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for _ in matchedIndexes:
                    name = data["names"]
                    counts[name] = counts.get(name, 0) + 1
                return max(counts, key=counts.get)
            return ""

    def save_photos(self, folder, count=10) -> bool:
        img_counter = 0
        if not os.path.exists(folder):
            os.makedirs(folder)
        while img_counter <= count:
            key = input("Press q to quit or ENTER to continue: ")
            if key == "q":
                break
            faces, frame = self.get_faces()
            if len(faces) == 0:
                print("No face detected, please try again")
                continue
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                img_name = "{}/{:04}.jpg".format(folder, img_counter)
                cv2.imwrite(img_name, frame[y: y + h, x: x + w])
                print("{} written!".format(img_name))
                img_counter += 1
        return True

    def set_dev(self):
        self.dev = None
        while self.dev is None:
            try:
                self.dev = int(input("Camera device id (leave blank for default for default)[0]: "))
            except ValueError as err:
                if str(err)[-2:] == "''":
                    self.dev = 0
                else:
                    print("Enter a number")
