from pathlib import Path
from tkinter import *
import cv2
from PIL import Image, ImageTk
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import time
import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from RecordAudio import *
import threading
from emotionIntegration import FirebaseLogger

BASE_DIR = Path(__file__).resolve().parent

firebase_logger = FirebaseLogger("../Integration/service-account.json")


flag = True


# --- STREAM MODE VARIABLE ---
# Set to "local" for your PC webcam or "pi" for the Raspberry Pi stream
STREAM_MODE = "pi"



# Convolutional Neural Network with layering and weights from VGG19 with further image classification training on the FER13 Dataset.
FER13_model = tf.keras.models.load_model(
    str(BASE_DIR / "model_FER13_VGG19.keras"),
    compile=False
)

# Convolutional Neural Network with layering and weights from VGG19 with further image classification training on the RAF Dataset.
RAF_model = tf.keras.models.load_model(
    str(BASE_DIR / "model_2.keras"),
    compile=False
)

haarcascade = cv2.CascadeClassifier(
    str(BASE_DIR / "haarcascade_frontalface_default.xml")
)

mapper = ['anger', 'disgust', 'fear', 'happiness', 'sadness', 'surprise', 'neutral']
frame_data = []

display_emotion = "neutral"        # Start emotion
candidate_emotion = "neutral"
candidate_count = 0
required_frames = 4       # Required frames with the same predicted shown emotion begore
alpha = 0.25              # Smoothing variable (lower = smoother transition between emotions)
stop_event = threading.Event()

prev_strengths = {
    "anger": 0.0,
    "disgust": 0.0,
    "fear": 0.0,
    "happiness": 0.0,
    "sadness": 0.0,
    "surprise": 0.0,
    "neutral": 0.0
}

color_c = {
    "anger":     (0, 0, 255),       # Red
    "disgust":   (0, 160, 0),       # Green
    "fear":      (180, 0, 180),     # Purple
    "happiness": (0, 255, 255),     # Yellow
    "sadness":   (255, 0, 0),       # Blue
    "surprise":  (0, 165, 255),     # Orange
    "neutral":   (180, 180, 180)    # Grey
}
session_start_time = 0
def preprocess_image_FER13(frame):
    img = cv2.resize(frame, (48, 48))
    img = img.astype("float32")
    return np.expand_dims(img, axis=0)

def preprocess_image_RAF(frame):
    img = cv2.resize(frame, (48, 48))
    img = img.astype("float32")
    img = tf.keras.applications.vgg19.preprocess_input(img)
    return np.expand_dims(img, axis=0)

def PredictionFaces(face, verbose_val):
    prediction_FER13 = FER13_model.predict(preprocess_image_FER13(face), verbose=verbose_val)
    prediction_RAF = RAF_model.predict(preprocess_image_RAF(face), verbose=verbose_val)

    anger = prediction_RAF[0][2]
    disgust = prediction_FER13[0][1]
    fear = prediction_FER13[0][2]
    happiness = prediction_FER13[0][3]
    sadness = prediction_RAF[0][4]
    surprise = prediction_FER13[0][5]
    neutral = prediction_FER13[0][6]

    emotions = np.array([anger, disgust, fear, happiness, sadness, surprise, neutral], dtype=np.float32)

    return emotions

def update_emotion_and_color(prediction):
    global display_emotion, candidate_emotion, candidate_count, prev_strengths

    total = np.sum(prediction)
    if total > 0:
        prediction = prediction / total

    raw_emotion = mapper[int(np.argmax(prediction))]

    if raw_emotion == display_emotion:
        candidate_emotion = raw_emotion
        candidate_count = 0
    else:
        if raw_emotion == candidate_emotion:
            candidate_count += 1
        else:
            candidate_emotion = raw_emotion
            candidate_count = 1

        if candidate_count >= required_frames:
            display_emotion = candidate_emotion
            candidate_count = 0

    strengths = {}
    for i, emotion_name in enumerate(mapper):
        current_value = prediction[i]
        smoothed_value = (1 - alpha) * prev_strengths[emotion_name] + alpha * current_value
        strengths[emotion_name] = smoothed_value

    prev_strengths = strengths.copy()

    color_list = []
    boost = 1.25   # boosts current emotion

    for i in range(3):  # B, G, R
        value = 0.0
        for emotion_name in mapper:
            strength = strengths[emotion_name]

            if emotion_name == display_emotion:
                strength *= boost

            value += strength * color_c[emotion_name][i]

        value = int(max(0, min(255, value)))
        color_list.append(value)

    color = tuple(color_list)

    return display_emotion, color, strengths

def plotColor(name,df):

    ax = plt.subplots(figsize=(18, 6))

    for i, row in df.iterrows():

        # Convert BGR to RGB and normalize to 0-1 for matplotlib
        bgr = row['color']
        rgb = (bgr[2]/255, bgr[1]/255, bgr[0]/255)
        ax.bar(i, row['max_score'], color=rgb, width=0.8)


    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['timestamp'], rotation=60, ha='right', fontsize=6)
    ax.set_ylabel('Max Score')
    ax.set_xlabel('Timestamp')
    ax.set_title(f'Facial emotion recognition of {name} ')
    plt.tight_layout()
    plt.show()


def faceRec(face, name, frame, x, y, w, h):

    emotion, color,strength = update_emotion_and_color(PredictionFaces(face, 0))
    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
    cv2.putText(frame, f"{name}: {emotion}", (x, y - 10 if y - 10 > 20 else y + h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    return color, strength

def to_row(color, all_strengths):
    global session_start_time
    elapsed_ms = int((time.time() - session_start_time) * 1000)
    timestamp = time.strftime("%T",(time.gmtime(time.time())))
    scores = list(all_strengths.values())
    max_score = max(scores)
    emotion_max = mapper[scores.index(max_score)]

    firebase_logger.update_current_emotion(emotion_max, max_score, elapsed_ms, color_bgr=color)

    row = [max_score,emotion_max,color,*scores,timestamp]
    frame_data.append(row)


def CameraStream(name, timestamp, record_flag_path=None):
    global session_start_time
    global flag
    global display_emotion  # Pulling this in to draw the text on skipped frames
    firebase_logger.get_active_session_id()
    
    # --- STEP 1 & 2: STREAM ROUTING AND BUFFER LIMIT ---
    if STREAM_MODE == "pi":
        print("[*] Connecting to Raspberry Pi video stream...")
        camera_source = "tcp://10.0.0.2:8160"
    else:
        print("[*] Using local webcam...")
        camera_source = 0
        
    camera = cv2.VideoCapture(camera_source)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Force OpenCV to drop old frames
    
    if not camera.isOpened():
        print(f"[!] Error: Could not open video source '{camera_source}'")
        return
    # ---------------------------------------------------

    frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    four_cc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(f'RecordingVideo{str(name).capitalize()}-{timestamp}.avi', four_cc, 20.0, (frame_width, frame_height))

    # Show camera preview while waiting for record signal
    print("[*] Camera ready. Waiting for record signal...")
    while record_flag_path and not os.path.exists(record_flag_path):
        ret, frame = camera.read()
        if not ret:
            continue
        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            camera.release()
            out.release()
            cv2.destroyAllWindows()
            return

    session_start_time = time.time()
    print("[*] Recording started.")

    # --- STEP 3: FRAME SKIPPING VARIABLES ---
    frame_counter = 0                 
    process_every_n_frames = 20        # Processes AI on 1 frame, skips the next 2
    last_known_emotions = {}          # Dictionary to cache colors, strengths, and text
    # ----------------------------------------

    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        frame_counter += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = haarcascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(96, 96))

        for num, (x, y, w, h) in enumerate(faces):
            # Create a basic ID to track faces between frames
            face_id = f"face_{num}" 

            # Only run the heavy models if it's the Nth frame OR a newly detected face
            if frame_counter % process_every_n_frames == 0 or face_id not in last_known_emotions:
                face = frame[y:y+h, x:x+w]
                
                # faceRec handles the prediction AND draws the bounding box/text
                max_color, all_strengths = faceRec(face, name, frame, x, y, w, h)
                
                # Save these results in our cache so we can use them on the skipped frames
                last_known_emotions[face_id] = (max_color, all_strengths, display_emotion)
                
                # Log data to firebase and arrays
                to_row(max_color, all_strengths)
            
            else:
                # SKIPPED FRAME: Do not run AI models. Just draw the cached graphics.
                max_color, _, cached_emotion = last_known_emotions[face_id]
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), max_color, 2)
                cv2.putText(frame, f"{name}: {cached_emotion}", (x, y - 10 if y - 10 > 20 else y + h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, max_color, 2)

        out.write(frame)
        cv2.imshow('Camera', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    camera.release()
    out.release()
    cv2.destroyAllWindows()

    columns = ["max_score","emotion","color","anger","disgust","fear","happiness","sadness","surprise","neutral","timestamp"]
    df = pd.DataFrame(frame_data, columns=columns)
    df.name = f'{str(name).capitalize()} | {timestamp}'
    print(df)
    plotColor(name, df)

def main():

    # File name
    # print("Enter your name:")
    # name = input()
    # timestamp = time.strftime("%Y-%m-%d_%H-%M",(time.gmtime(time.time())))    
    
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else input("Enter your name: ")
    timestamp = time.strftime("%Y-%m-%d_%H-%M", (time.gmtime(time.time())))
    record_flag_path = sys.argv[2] if len(sys.argv) > 2 else None

#   Run audio recording in a seperate thread
    t = threading.Thread(target=recordAudio,args=(name,timestamp,stop_event))
    #t.start()

    CameraStream(name, timestamp, record_flag_path)
    print("Press enter to finish recording.")

#    Wait for video recording to finish
    t.join()

if __name__ == "__main__":
    main()
