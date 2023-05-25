# imports libraries and packages
import cv2
import face_recognition
import os
import glob
import numpy as np
from imutils.video import VideoStream
import time

# initializes the video stream with picamera
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

known_face_encodings = []
known_face_names = []

# resizes frame for a faster speed
frame_resizing = 0.25

def load_encoding_images(images_path):
    # loads images
    images_path = glob.glob(os.path.join(images_path, "*.*"))

    print("{} encoding images found.".format(len(images_path)))

    # stores image encoding and names
    for img_path in images_path:
        img = cv2.imread(img_path)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # gets the filename only from the initial file path
        basename = os.path.basename(img_path)
        (filename, ext) = os.path.splitext(basename)
        
        # gets encoding
        img_encoding = face_recognition.face_encodings(rgb_img)[0]

        # stores file name and file encoding
        known_face_encodings.append(img_encoding)
        known_face_names.append(filename)
    print("Encoding images loaded")

def detect_known_faces(frame, detectedName):
    small_frame = cv2.resize(frame, (0, 0), fx=frame_resizing, fy=frame_resizing)
    # finds all the faces and face encodings in the current frame of video
    # converts the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    
    for face_encoding in face_encodings:
        # sees if the face is a match for the known face
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # uses the first one
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            
        if detectedName == name:
            return True

def detectionstop():
    vs.stop()

def detection(detectedName):
    while True:
        frame = vs.read()

        # detects faces
        faceDetected = detect_known_faces(frame, detectedName)
        
        return faceDetected

# encodes faces from a folder
load_encoding_images("images/")