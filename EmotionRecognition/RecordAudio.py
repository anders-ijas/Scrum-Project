import sounddevice as sd
import numpy as np
import wave

from EmotionalRecognition import *

def recordAudio(name="unnamed",timestamp="",stop_event=None):
    channels = 1 ## Kan behöva ändras till två beroende på system, 1 på mac
    fs = 44100
    frames = []

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    print("Recording has started.")
    print("Press enter to stop.")
    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
        while not stop_event.is_set():
            sd.sleep(100)

    print("Recording stopped.")
    audio = np.concatenate(frames, axis=0)

    sample_format = ((np.int16(audio * 32767)).tobytes())
    with wave.open(f"RecordingAudio{str(name).capitalize()}-{timestamp}.wav", "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(sample_format)
