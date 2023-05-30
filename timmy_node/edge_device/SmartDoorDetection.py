# imports libraries
import pickle
from imutils.video import VideoStream
import face_recognition
from datetime import datetime
import imutils
import time

# 'Countdown' function to countdown the time for face recognition
def Countdown(timeDetectionStart):
    timeElapsed = datetime.now() - timeDetectionStart
    timeElapsedMs = (timeElapsed.days * 24 * 60 * 60 + timeElapsed.seconds) * 1000 + timeElapsed.microseconds / 1000.0
    
    return int(timeElapsedMs)

# 'detection' function to be called in SmartDoorSerial.py
def detection(detectedName, timeDetected, timeDetectionStart, timeFaceDetection):
    result = False
    
    # initializes the video stream with picamera
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)
    
    # runs while the face recognition duration is not over
    while (Countdown(timeDetectionStart) - timeDetected <= (timeFaceDetection + 2) * 1000):
        # determines faces from encodings.pickle file model created from SmartDoorTraining.py
        encodingsP = "encodings.pickle"

        # loads the known faces and embeddings
        data = pickle.loads(open(encodingsP, "rb").read())
        
        # grabs the frame from the threaded video stream and resizes it to 500px to speed up processing
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        
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
                # finds the indexes of all matched faces
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]

                # loops over the matched indexes
                for i in matchedIdxs:
                    name = data["names"][i]
                
                # checks if the person detected is the person who is at the door
                if detectedName == name:
                    result = True
                    break
                
        if result is True:
            break
        
    vs.stop()
    
    return result