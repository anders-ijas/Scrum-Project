import sounddevice as sd
import numpy as np
import wave
import shutil

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
        
def copy_audio_to_transcription_input(original_filepath):
    import os
    import shutil   
    from datetime import datetime
    
    input_dir = "transcription/input"
    os.makedirs(input_dir, exist_ok=True)
    
    # Generera unikt filnamn baserat på tid
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}.wav"
    destination_path = os.path.join(input_dir, filename)
    
    shutil.copy(original_filepath, destination_path)
    print(f"Audio file copied to: {destination_path}")
    return filename