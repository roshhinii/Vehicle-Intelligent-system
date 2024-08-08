import time
import firebase_admin
import RPi.GPIO as GPIO
import cv2
import dlib
import imutils
import random
from imutils import face_utils
from scipy.spatial import distance as dist
from threading import Thread
from firebase_admin import credentials, initialize_app, db


# INPUT PINS INITIALIZATION
GPIO.setmode(GPIO.BCM)
# accelaration
acc_pin1 = 2
acc_pin2 = 3
# brake pins
brake_pin1 = 4
brake_pin2 = 18
# seat belt
seatbelt_pin = 17
# BPM
bpm_pin = 27
# steering
steering_pin = 9
# left - right - in
left_in_pin = 5
right_in_pin = 0
# headlight in
headlight_in_pin = 6
# gear
gear_pin1 = 20
gear_pin2 = 21
# cornering
cornering_pin1 = 16
cornering_pin2 = 12
# sudden break
sudden_break_pin = 10
# horn
horn_pin = 27
# beep out
beep_out_pin = 22
# headlight out
headlight_out_pin = 8
# left - right - out
left_out_pin = 24
right_out_pin = 25


# outputs
GPIO.setup(beep_out_pin, GPIO.OUT)
GPIO.setup(headlight_out_pin, GPIO.OUT)
GPIO.setup(left_out_pin, GPIO.OUT)
GPIO.setup(right_out_pin, GPIO.OUT)
# inputs
GPIO.setup(acc_pin1, GPIO.IN)
GPIO.setup(acc_pin2, GPIO.IN)
GPIO.setup(brake_pin1, GPIO.IN)
GPIO.setup(brake_pin2, GPIO.IN)
GPIO.setup(seatbelt_pin, GPIO.IN)
GPIO.setup(steering_pin, GPIO.IN)
GPIO.setup(left_in_pin, GPIO.IN)
GPIO.setup(right_in_pin, GPIO.IN)
GPIO.setup(headlight_in_pin, GPIO.IN)
GPIO.setup(gear_pin1, GPIO.IN)
GPIO.setup(gear_pin2, GPIO.IN)
GPIO.setup(cornering_pin1, GPIO.IN)
GPIO.setup(cornering_pin2, GPIO.IN)
GPIO.setup(sudden_break_pin, GPIO.IN)
GPIO.setup(horn_pin, GPIO.IN)

#
FACIAL_LANDMARK_PREDICTOR = "/home/pi/Desktop/Cockpit-Intelligence/shape_predictor_68_face_landmarks.dat"  # path to dlib's pre-trained facial landmark predictor
MINIMUM_EAR = 0.2    # Minimum EAR for both the eyes to mark the eyes as open
MAXIMUM_FRAME_COUNT = 10

#Initializations
faceDetector = dlib.get_frontal_face_detector()     # dlib's HOG based face detector
landmarkFinder = dlib.shape_predictor(FACIAL_LANDMARK_PREDICTOR)  # dlib's landmark finder/predcitor inside detected face
webcamFeed = cv2.VideoCapture(0)

# Finding landmark id for left and right eyes
(leftEyeStart, leftEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rightEyeStart, rightEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

def eye_aspect_ratio(eye):
    p2_minus_p6 = dist.euclidean(eye[1], eye[5])
    p3_minus_p5 = dist.euclidean(eye[2], eye[4])
    p1_minus_p4 = dist.euclidean(eye[0], eye[3])
    ear = (p2_minus_p6 + p3_minus_p5) / (2.0 * p1_minus_p4)
    return ear

EYE_CLOSED_COUNTER = 0



cred = credentials.Certificate("/home/pi/Desktop/Cockpit-Intelligence/cockpit-intelligence-firebase-adminsdk-a7ryd-7da4f325ef.json")
firebase_app = initialize_app(cred, {"databaseURL": "https://cockpit-intelligence-default-rtdb.firebaseio.com/"})
ref = db.reference("/rpi_sensor")


print("Send Data to Firebase Using Raspberry Pi")
print("----------------------------------------")
print()


def earCalculation():
    earCalculation.ear_val = 0
    
    while True:
        (status, image) = webcamFeed.read()
        image = imutils.resize(image, width=800)
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = faceDetector(grayImage, 0)


        for face in faces:
            faceLandmarks = landmarkFinder(grayImage, face)
            faceLandmarks = face_utils.shape_to_np(faceLandmarks)

            leftEye = faceLandmarks[leftEyeStart:leftEyeEnd]
            rightEye = faceLandmarks[rightEyeStart:rightEyeEnd]

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0
            earCalculation.ear_val = ear

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)

            cv2.drawContours(image, [leftEyeHull], -1, (255, 0, 0), 2)
            cv2.drawContours(image, [rightEyeHull], -1, (255, 0, 0), 2)

            if ear < MINIMUM_EAR:
                EYE_CLOSED_COUNTER += 1
            else:
                EYE_CLOSED_COUNTER = 0

            cv2.putText(image, "EAR: {}".format(round(ear, 1)), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            #cv2.putText(image, "Distraction: {}".str(dis), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if EYE_CLOSED_COUNTER >= MAXIMUM_FRAME_COUNT:
                cv2.putText(image, "Drowsiness", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Frame", image)
        cv2.waitKey(1)


def parametersCalculation():
    acc = 0
    brake = 0
    seatbelt = 0
    steering = 0
    left_in = 0
    right_in = 0
    headlightin = 0
    gear = 0
    cornering = 0
    sudden_break = 0
    horn = 0

    while True:
        # acc calc
        if((GPIO.input(acc_pin1) == 0) and (GPIO.input(acc_pin2) == 1)):
            acc = 1
        elif((GPIO.input(acc_pin1) == 1) and (GPIO.input(acc_pin2) == 0)):
            acc = 2
        elif((GPIO.input(acc_pin1) == 1) and (GPIO.input(acc_pin2) == 1)):
            acc = 3
        elif((GPIO.input(acc_pin1) == 0) and (GPIO.input(acc_pin2) == 0)):
            acc = 0

        # brake calc
        if((GPIO.input(brake_pin1) == 0) and (GPIO.input(brake_pin2) == 1)):
            brake = 1
        elif((GPIO.input(brake_pin1) == 1) and (GPIO.input(brake_pin2) == 0)):
            brake = 2
        elif((GPIO.input(brake_pin1) == 1) and (GPIO.input(brake_pin2) == 1)):
            brake = 3
        elif((GPIO.input(brake_pin1) == 0) and (GPIO.input(brake_pin2) == 0)):
            brake = 0

        # seatbelt calc
        if(GPIO.input(seatbelt_pin) == 0):
            seatbelt = 1
            GPIO.output(beep_out_pin, GPIO.HIGH)
        elif(GPIO.input(seatbelt_pin) == 1):
            seatbelt = 0
            GPIO.output(beep_out_pin, GPIO.LOW)

        # steering calc
        if(GPIO.input(steering_pin) == 1):
            steering = 0
        elif(GPIO.input(steering_pin) == 0):
            steering = 1

        # left-in calc
        if(GPIO.input(left_in_pin) == 1):
            if(left_in==0):
                left_in=1
            else:
                left_in=0

        # right-in calc
        if(GPIO.input(right_in_pin) == 1):
            if(right_in==0):
                right_in=1
            else:
                right_in=0

        # headlight in calc
        if(GPIO.input(headlight_in_pin) == 1):
            if(headlightin==0):
                headlightin=1
            else:
                headlightin=0

                
        # gear calc
        if((GPIO.input(gear_pin1) == 0) and (GPIO.input(gear_pin2) == 1)):
            time.sleep(.250)
            gear+=1
        elif((GPIO.input(gear_pin1) == 1) and (GPIO.input(gear_pin2) == 0)):
            time.sleep(.250)
            gear-=1
        if(gear<0):
            gear=0
        if(gear>5):
            gear=5


        # cornering calc
        if((GPIO.input(cornering_pin1) == 0) and (GPIO.input(cornering_pin2) == 1)):
            cornering = 1
        elif((GPIO.input(cornering_pin1) == 1) and (GPIO.input(cornering_pin2) == 0)):
            cornering = 2
        elif((GPIO.input(cornering_pin1) == 0) and (GPIO.input(cornering_pin2) == 0)):
            cornering = 0
        
        # sudden break calc
        if(GPIO.input(sudden_break_pin) == 1):
            sudden_break = 1
        elif(GPIO.input(sudden_break_pin) == 0):
            sudden_break = 0
        
        # horn calc
        if(GPIO.input(horn_pin) == 1):
            horn = 1
        elif(GPIO.input(horn_pin) == 0):
            horn = 0
            
        
         # headlight out calc
        if(GPIO.input(headlight_in_pin) == 1):
            if(headlightin==0):
                GPIO.output(headlight_out_pin, GPIO.HIGH)
            else:
                GPIO.output(headlight_out_pin, GPIO.LOW)
                
        
        # left-out calc
        if(GPIO.input(left_in_pin) == 1):
            if(left_in==0):
                GPIO.output(left_out_pin, GPIO.HIGH)
            else:
                GPIO.output(left_out_pin, GPIO.LOW)


        # right-out calc
        if(GPIO.input(right_in_pin) == 1):
            if(right_in==0):
                GPIO.output(right_out_pin, GPIO.HIGH)
            else:
                GPIO.output(right_out_pin, GPIO.LOW)
        
                
        data={
      "ear":earCalculation.ear_val,
      "acceleration":acc,
      "brake":brake,
      "seatbelt":seatbelt,
      "steering":steering,
      "left_in":left_in,
      "right_in":right_in,
      "headlight":headlightin,
      "gear":gear,
      "cornering":cornering,
      "sudden break":sudden_break,
      "horn":horn
        }
        print(data)
        ref.child("rpi_sensors").set(data)


if _name_ == '_main_':
    Thread(target = earCalculation).start()
    Thread(target = parametersCalculation).start()
