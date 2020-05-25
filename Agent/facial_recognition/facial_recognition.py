import os
import cv2



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

def get_camera(device_id):
    c = cv2.VideoCapture(device_id)
    c.set(3, 640)
    c.set(4, 480)
    return c


class FaceDetectionEngine:

    def __init__(self, controller):
        # TODO implement FaceDetectionEngine
        dev = None
        while not dev:
            try:
                dev = int(input("Camera device id (leave blank for default for default)[0]: "))
            except ValueError as err:
                if str(err)[-2:]=="''":
                    dev = 0
                else:
                    print("Enter a number")
        self.controller = controller
        self.camera = get_camera(dev)
        self.classifier = cv2.CascadeClassifier()
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
                ret, frame = self.camera.read()
            faces = self.detect_face(frame)
        return faces, frame

    def encode_face(self, path):
        for i, image_path in enumerate(os.walk(path)):
            if image_path[-4:] in [".jpg", "jpeg"]:
                image = cv2.imread(image_path)
            else:
                continue
            name = os.path.basename(image_path[-1])
            rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    def compare_face(self, user) -> bool:
        # TODO implement me
        faces = self.get_faces()[0]
        return bool(self)

    def save_photos(self, folder, count=10):
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
