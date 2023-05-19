import pickle
from imutils.video import VideoStream
import face_recognition
import time

# determines faces from encodings.pickle file model created from training.py
encodingsP = "encodings.pickle"

# loads the known faces and embeddings along with OpenCV's Haar cascade for face detection
data = pickle.loads(open(encodingsP, "rb").read())

# initializes the video stream with picamera
vs = VideoStream(usePiCamera=True).start()

time.sleep(2.0)

def detection(detectedName):
    # grabs the frame from the threaded video stream and resizes it to 500px to speedup processing
    frame = vs.read()
    
    # detects the face boxes
    boxes = face_recognition.face_locations(frame)
    
    # computes the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(frame, boxes)

    # loops over the facial embeddings
    for encoding in encodings:
        # attempts to match each face in the input image to the known encodings
        matches = face_recognition.compare_faces(data["encodings"], encoding)

        # checks if there is a match
        if True in matches:
            # finds the indexes of all matched faces and initializes a dictionary to count the total number of times each face was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]

            # loops over the matched indexes and maintains a count for each recognized face
            for i in matchedIdxs:
                name = data["names"][i]
            
            # checks if the person detected is the person who is at the door
            if detectedName == name:
                return True
            
def detectionstop():
    vs.stop()