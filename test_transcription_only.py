import os
import subprocess
import sounddevice as sd
import numpy as np
import wave
import uuid
import sys
from datetime import datetime
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

def simple_record():
    print("=" * 60)
    print("🎤 RECORD → TRANSCRIBE")
    print("=" * 60)
    
    channels = 1
    fs = 44100
    frames = []
    
    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())
    
    input("\nPress ENTER to START recording...")
    print("🔴 RECORDING...")
    
    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
        input("\nPress ENTER to STOP recording...")
    
    print("Stopping...")
    audio = np.concatenate(frames, axis=0)
    
    input_dir = "transcription/input"
    os.makedirs(input_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.wav"
    filepath = os.path.join(input_dir, filename)
    
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    
    print(f"✅ Saved: {filepath}")
    return filename

def transcribe(filename):
    print(f"\n📝 Transcribing: {filename}")
    
    result = subprocess.run(
        [sys.executable, "transcribe.py", filename],
        cwd="transcription",
        capture_output=True,
        text=True
    )
    
    # Print only the JSON result (the last line that starts with {)
    for line in result.stdout.strip().split('\n'):
        if line.startswith('{'):
            print("\n" + "=" * 60)
            print("📝 RESULT")
            print("=" * 60)
            print(line)
            break

if __name__ == "__main__":
    filename = simple_record()
    transcribe(filename)