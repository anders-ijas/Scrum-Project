import socket
import subprocess
import time

# Konfiguration
HOST = '10.0.0.1'  # Datorns IP-adress
PORT = 65432       # Port att lyssna på

def main():
    # Sätt upp socket-servern
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Tillåt snabb återanvändning av porten om skriptet startas om
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    print(f"Lyssnar efter knapptryck på {HOST}:{PORT}...")

    is_recording = False
    emotion_process = None
    audio_process = None
    audio_file = "current_recording.mp3"

    while True:
        # Väntar på anslutning från RPI4
        conn, addr = server_socket.accept()
        with conn:
            data = conn.recv(1024)
            if not data:
                continue
            
            command = data.decode('utf-8').strip()
            
            if command == 'TOGGLE':
                if not is_recording:
                    print("\n[+] Signal mottagen: STARTAR processer")
                    
                    # 1. Starta Emotion Recognition
                    emotion_process = subprocess.Popen(["python", "EmotionalRecognition.py"])
                    
                    # 2. Starta ljudinspelning
                    # Byt ut "record_audio.py" mot hur du faktiskt spelar in ljudet.
                    # Alternativt ffmpeg-kommando: subprocess.Popen(["ffmpeg", "-f", "dshow", "-i", "audio=Microphone Name", audio_file])
                    audio_process = subprocess.Popen(["python", "record_audio.py", audio_file])
                    
                    is_recording = True
                    
                else:
                    print("\n[-] Signal mottagen: STOPPAR processer")
                    
                    # 1. Stoppa Emotion Recognition och Inspelning
                    if emotion_process:
                        emotion_process.terminate()
                        emotion_process.wait() # Vänta tills processen stängts ordentligt
                        
                    if audio_process:
                        audio_process.terminate()
                        audio_process.wait()
                        
                    print("[*] Processer stoppade. Startar transkribering...")
                    
                    # 2. Starta transkriberingsprogrammet
                    # Popen används här så transkriberingen kan köras i bakgrunden 
                    # medan servern är redo att ta emot nästa knapptryck direkt.
                    subprocess.Popen(["python", "transcribe.py", audio_file])
                    
                    is_recording = False
                    print("[*] Återgår till vänteläge för nästa iteration...")

if __name__ == "__main__":
    main()