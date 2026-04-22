from tkinter import *
import cv2
from PIL import Image, ImageTk
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Input,Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Layer
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import cv2
from PIL import Image, ImageTk


camera = cv2.VideoCapture(0)
frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
four_cc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', four_cc,20.0,(frame_width,frame_height))
last_label = ""

## Used to predict X, Y, Z
FER13_model = tf.keras.models.load_model("/Users/alexanderknave/Desktop/KTH/Projekt/model_FER13_VGG19.keras", compile=False)

## Used to predict X, Y, Z
RAF_model = tf.keras.models.load_model("/Users/alexanderknave/Desktop/KTH/Projekt/RAF_model_2.keras", compile=False)

haarcascade = cv2.CascadeClassifier("/Users/alexanderknave/Desktop/KTH/Projekt/haarcascade_frontalface_default.xml")

mapper = ['anger','disgust','fear','happiness','sadness','surprise','neutral']

def preprocess_image_FER13(frame):
    img = cv2.resize(frame,(48,48))
    img = img.astype("float32")
    return np.expand_dims(img, axis=0)

def preprocess_image_RAF(frame):
    img = cv2.resize(frame, (100, 100))
    img = img.astype("float32")
    img = tf.keras.applications.vgg19.preprocess_input(img)
    return np.expand_dims(img, axis=0)

def PredictionFaces(face,verbose_val):
    anger = 0
    disgust = 0
    fear = 0
    happiness = 0
    sadness = 0
    surprise = 0
    neutral = 0

    ## FER13: Med score > 0 && Neutral
    ## Gör dessa bra: Neutral (för bra), Happiness, Sadness
    ## Gör OK: Surprised (om den överdrivs), Disgust (om den överdrivs)
    ## Gör inte bra: Fear, Anger

    ## FER13: Med score > 0.5 && Neutral
    ## Gör dessa bra: Neutral (*), Happiness (*)
    ## Gör OK: Sadness, Surprised (om den överdrivs)(*),fear (om den överdrivs)(*), Disgust (om den överdrivs)(*)
    ## Gör inte bra: Anger

    prediction_FER13 = FER13_model.predict(preprocess_image_FER13(face),verbose_val)

    ## RAF 2: Med score > 0.0 && Neutral
    ## Gör dessa bra: Anger, Neutral (för bra), Sadness, Happiness
    ## Gör OK:
    ## Gör inte bra: , Surprised, fear, disgust

    ## RAF 2: Med score > 0.5 && Neutral
    ## Gör dessa bra: Happiness (på gränsen at åka ut), Sadness(!), Anger(!)
    ## Gör OK:
    ## Gör inte bra: disgust, Surprised, fear

    prediction_RAF = RAF_model.predict(preprocess_image_RAF(face),verbose_val)

    ## Add predictions
    anger = prediction_RAF[0][2]
    disgust = prediction_FER13[0][1]
    fear = prediction_FER13[0][2]
    happiness = prediction_FER13[0][3]
    sadness =  prediction_RAF[0][4]
    surprise = prediction_FER13[0][5]
    neutral = prediction_FER13[0][6]

    emotions = [anger,disgust,fear,happiness,sadness,surprise,neutral]
    emotions_no_neutral = {anger,disgust,fear,happiness,sadness,surprise}

    #strongest_emotion = np.argmax(emotions)
    #strongest_emotion_no_neutral = np.argmax(emotions_no_neutral)

    return emotions


def CameraStream():
    global counter, last_label

    ret, frame = camera.read()

    if not ret:
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = haarcascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(96, 96)
    )

    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]

        prediction = PredictionFaces(face,2)
        print(prediction)
        print(f'Print ArgMax: {np.argmax(prediction)}')


        if np.argmax(prediction) > 0.0:
            last_label = mapper[np.argmax(prediction)]
            print(f'Print last_label: {last_label}')

        cv2.rectangle(frame, (x, y), (x+w, y+h), (255,255,255), 2)
        cv2.putText(frame, last_label,(int(frame_width/2),int(frame_height/2)),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),2)
    out.write(frame)
    cv2.imshow('Camera',frame)

while True:

    CameraStream()

    if cv2.waitKey(1) == ord('q'):
        break

camera.release()
out.release()
cv2.destroyAllWindows()

root = Tk();
root.title("Test window");
root.geometry("1000x500")

root.mainloop();
