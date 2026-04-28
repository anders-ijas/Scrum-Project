import socket
import subprocess
import sys
import os

# Konfiguration
HOST = '10.0.0.1'  # Datorns IP-adress
PORT = 65432       # Port att lyssna på

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    print(f"Lyssnar efter knapptryck på {HOST}:{PORT}...")

    is_recording = False
    emotion_process = None
    audio_process = None
    audio_file = "current_recording.mp3"
    
    # Detta är magin som löser "ModuleNotFoundError"
    python_path = sys.executable 

    while True:
        conn, addr = server_socket.accept()
        with conn:
            data = conn.recv(1024)
            if not data:
                continue
            
            command = data.decode('utf-8').strip()
            
            if command == 'TOGGLE':
                if not is_recording:
                    print("\n[+] Signal mottagen: STARTAR processer")
                    
                    # Kör skripten med dina egna fungerande sökvägar. 
                    # Uppdatera dessa till exakt det du använde när datorn faktiskt hittade filerna.
                    emotion_process = subprocess.Popen([python_path, "../EmotionRecognition/EmotionalRecognition.py"])
                    audio_process = subprocess.Popen([python_path, "../Integration/record_audio.py", audio_file])
                    
                    is_recording = True
                    
                else:
                    print("\n[-] Signal mottagen: STOPPAR processer")
                    
                    if emotion_process:
                        emotion_process.terminate()
                        emotion_process.wait() 
                        
                    if audio_process:
                        audio_process.terminate()
                        audio_process.wait()
                        
                    print("[*] Processer stoppade. Startar transkribering...")
                    
                    subprocess.Popen([python_path, "../transcription/transcribe.py", audio_file])
                    
                    is_recording = False
                    print("[*] Återgår till vänteläge för nästa iteration...")

if __name__ == "__main__":
    main()