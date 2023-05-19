import cv2
from picamera import PiCamera
import os
import mysql.connector
import time
from imutils import paths
import face_recognition
import pickle
from imutils.video import VideoStream
        
counter = 0
counterThreshold = 10

cam = PiCamera()
cam.resolution = (512, 304)
cam.framerate = 30

mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Door")
mycursor = mydb.cursor()
mycursor.execute("SELECT name FROM Profile ORDER BY profile_id DESC")
latestName = mycursor.fetchone()
mycursor.close()

# create folder to store photos of user
if not os.path.exists('dataset/' + latestName[0]):
   os.makedirs('dataset/' + latestName[0])

def frames(captureNow):
    global counter
    print(counter)
    if counter >= counterThreshold - 1:
        training()
    
    img_name = "dataset/"+ latestName[0] +"/image_{}.jpg".format(counter)
    
    while True:
        if captureNow == False:
            frame = "/tmp/frame.jpg"
        else:
            frame = img_name
            counter += 1
            captureNow = False
        
        try:
            cam.capture(frame, format='jpeg')
            time.sleep(0.2)
            with open(frame, 'rb') as f:
                yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + f.read() + b'\r\n'
        except Exception as e:
            pass

        time.sleep(0.2)
        
def picturecounter():
    return counter + 1

def training():
    # images located in the dataset folder
    imagePaths = list(paths.list_images("dataset"))

    # initializes the list of known encodings and known names
    knownEncodings = []
    knownNames = []

    # loops over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extracts the person name from the image path
        name = imagePath.split(os.path.sep)[-2]

        # loads the input image and convert it from RGB (OpenCV ordering) to dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detects the (x, y)-coordinates of the bounding boxes corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb, model="hog")

        # computes the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)

        # loops over the encodings
        for encoding in encodings:
            # add each encoding + name to our set of known names and encodings
            knownEncodings.append(encoding)
            knownNames.append(name)

    # dumps the facial encodings + names to disk
    data = {"encodings": knownEncodings, "names": knownNames}
    f = open("encodings.pickle", "wb")
    f.write(pickle.dumps(data))
    f.close()