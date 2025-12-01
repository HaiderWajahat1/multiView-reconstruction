# feature_detection.py
import cv2
import numpy as np

def feature_detector(method='SIFT', nfeatures=4000):
    method = method.upper()
    if method == 'SIFT':
        detector = cv2.SIFT_create(
            nfeatures=nfeatures,
            contrastThreshold=0.03,
            edgeThreshold=10,
            sigma=1.6
        )
        return detector, 'SIFT'
    detector = cv2.ORB_create(nfeatures=nfeatures)
    return detector, 'ORB'


def detect_features(detector, image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return detector.detectAndCompute(gray, None)
