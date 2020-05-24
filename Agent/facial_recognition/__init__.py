try:
    from .facial_recognition import FaceDetectionEngine
except:
    from unittest.mock import Mock as FaceDetectionEngine