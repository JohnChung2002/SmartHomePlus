# imports libraries and packages
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Door")
mycursor = mydb.cursor()
mycursor.execute("SELECT name FROM Profile")
profileName = mycursor.fetchone()

name = profileName[0]

cam = PiCamera()
cam.resolution = (512, 304)
cam.framerate = 10
rawCapture = PiRGBArray(cam, size=(512, 304))
    
img_counter = 0

while True:
    for frame in cam.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        cv2.imshow("Take Photo [Press SPACE key]", image)
        rawCapture.truncate(0)
    
        k = cv2.waitKey(1)
        rawCapture.truncate(0)
        
        # press ESC KEY on keyboard to exit
        if k%256 == 27:
            break
        # press SPACE KEY on keyboard to take a picture
        elif k%256 == 32:
            img_name = "dataset/"+ name +"/image_{}.jpg".format(img_counter)
            cv2.imwrite(img_name, image)
            print("{} written!".format(img_name))
            img_counter += 1
         
    # press ESC KEY on keyboard to exit
    if k%256 == 27:
        break

cv2.destroyAllWindows()