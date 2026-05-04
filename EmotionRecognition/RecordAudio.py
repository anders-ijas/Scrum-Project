import sounddevice as sd
import numpy as np
import wave
import os
import sys
from datetime import datetime

# Dynamically find project root (assuming this file is in emotionrecognition folder)
def get_project_root():
    """Find project root by looking for transcription folder"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up until we find the transcription folder or hit drive root
    while current_dir != os.path.dirname(current_dir):  # Stop at drive root
        if os.path.exists(os.path.join(current_dir, "transcription")):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    # Fallback: go up one level from emotionrecognition (if run from there)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = get_project_root()

def recordAudio(name="unnamed", timestamp="", stop_event=None):
    channels = 1
    fs = 44100
    frames = []

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    print("Recording has started.")
    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
        while not stop_event.is_set():
            sd.sleep(100)

    print("Recording stopped.")
    audio = np.concatenate(frames, axis=0)

    sample_format = ((np.int16(audio * 32767)).tobytes())
    
    # Save to transcription/input folder
    target_dir = os.path.join(PROJECT_ROOT, "transcription", "input")
    os.makedirs(target_dir, exist_ok=True)
    
    filename = f"{timestamp}.wav"
    filepath = os.path.join(target_dir, filename)
    
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(sample_format)
    
    print(f"✅ Audio saved to: {filepath}")
    
    # Run transcription
    transcribe_script = os.path.join(PROJECT_ROOT, "transcription", "transcribe.py")
    import subprocess
    result = subprocess.run(
        [sys.executable, transcribe_script, filename],
        cwd=os.path.join(PROJECT_ROOT, "transcription"),
        capture_output=True,
        text=True
    )
    print("📝 Transcription result:")
    print(result.stdout)
    
    return filepath

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "unnamed"
    timestamp = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime("%Y%m%d_%H%M%S")
    stop_event = threading.Event()
    
    recorder_thread = threading.Thread(target=recordAudio, args=(name, timestamp, stop_event))
    recorder_thread.start()
    
    input()
    stop_event.set()
    recorder_thread.join()  