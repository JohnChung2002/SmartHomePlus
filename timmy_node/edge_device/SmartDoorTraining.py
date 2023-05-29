# imports libraries
from imutils import paths
import face_recognition
import pickle
import cv2
import os

# images located in the 'dataset' folder in the same directory
print("[INFO] start processing faces...")
imagePaths = list(paths.list_images("dataset"))

# initializes the list of known encodings and known names
knownEncodings = []
knownNames = []

# loops over the image paths
for (i, imagePath) in enumerate(imagePaths):
    # extracts the person name from the image path
    print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
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
        # adds each encoding + name to the set of known names and encodings
        knownEncodings.append(encoding)
        knownNames.append(name)

# dumps the facial encodings + names to disk
print("[INFO] serializing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}
f = open("encodings.pickle", "wb")
f.write(pickle.dumps(data))
f.close()