import socket
import subprocess
import sys
import os
import threading
import time
import keyboard
from datetime import datetime

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))  # integration folder
project_root = os.path.dirname(current_dir)               # Scrum-Project folder
emotion_path = os.path.join(project_root, "emotionrecognition")

# Add to sys.path so we can import RecordAudio
sys.path.insert(0, emotion_path)

# Debug prints
print(f"[*] Added to path: {emotion_path}")
print(f"[*] Files in emotionrecognition: {os.listdir(emotion_path) if os.path.exists(emotion_path) else 'NOT FOUND'}")

from RecordAudio import recordAudio
print("[*] RecordAudio imported successfully!")

# Konfiguration
DESIRED_HOST = '10.0.0.1'
PORT = 65432

def get_valid_host(target_ip):
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.bind((target_ip, 0)) 
        test_sock.close()
        return target_ip
    except OSError:
        print(f"[*] {target_ip} hittades inte på denna dator. Fallback till 127.0.0.1 (localhost).")
        return '127.0.0.1'

HOST = get_valid_host(DESIRED_HOST)

def send_local_toggle():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        client_socket.sendall(b'TOGGLE')
        client_socket.close()
    except Exception as e:
        print(f"\n[!] Manuellt avbrott misslyckades: {e}")

def listen_for_spacebar():
    keyboard.add_hotkey('space', send_local_toggle)
    keyboard.wait()

listener_thread = threading.Thread(target=listen_for_spacebar, daemon=True)
listener_thread.start()

# Rensa gamla flag-filer
for f in os.listdir(project_root):
    if f.startswith("record_") and f.endswith(".flag"):
        os.remove(os.path.join(project_root, f))

# Starta kameran direkt
current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
record_flag_path = os.path.join(project_root, f"record_{current_timestamp}.flag")
emotion_script = os.path.join(project_root, "emotionrecognition", "EmotionalRecognition.py")
emotion_process = subprocess.Popen([sys.executable, emotion_script, "recording", record_flag_path])
print("[*] Kamera startad automatiskt.")

def main():
    global record_flag_path
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Lyssnar efter knapptryck på {HOST}:{PORT}... (Tryck SPACE för att starta/stoppa inspelning)")

    is_recording = False
    audio_stop_event = None
    audio_thread = None

    while True:
        conn, addr = server_socket.accept()
        with conn:
            data = conn.recv(1024)
            if not data:
                continue
            
            command = data.decode('utf-8').strip()
            
            if command == 'TOGGLE':
                if not is_recording:
                    print("\n[+] Signal mottagen: STARTAR inspelning")

                    open(record_flag_path, 'w').close()

                    audio_stop_event = threading.Event()
                    audio_thread = threading.Thread(
                        target=recordAudio,
                        args=("recording", current_timestamp, audio_stop_event)
                    )
                    audio_thread.start()
                    
                    is_recording = True
                    
                    print("[*] Inspelning startad.")
                else:
                    print("\n[-] Signal mottagen: STOPPAR inspelning")

                    if emotion_process:
                        emotion_process.terminate()
                        emotion_process.wait() 
                    
                    if audio_stop_event:
                        audio_stop_event.set()
                    
                    if audio_thread:
                        audio_thread.join()

                    if record_flag_path and os.path.exists(record_flag_path):
                        os.remove(record_flag_path)

                    print(f"[*] Audio saved to: transcription/input/{current_timestamp}.wav")
                    
                    is_recording = False
                    print("[*] Färdig. Återgår till vänteläge...")

if __name__ == "__main__":
    main()
