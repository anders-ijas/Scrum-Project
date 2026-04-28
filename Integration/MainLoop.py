import socket
import subprocess
import sys
import os
import threading
import keyboard

# Konfiguration
DESIRED_HOST = '10.0.0.1'  # Den IP vi helst vill använda
PORT = 65432               # Port att lyssna på

# --- NYTT: AUTOMATISK IP-KONTROLL ---
def get_valid_host(target_ip):
    """Testar om target_ip tillhör datorn. Om inte, returnera localhost."""
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Port 0 låter OS välja en tillfällig ledig port. 
        # Vi gör detta enbart för att se om IP-adressen är giltig.
        test_sock.bind((target_ip, 0)) 
        test_sock.close()
        return target_ip
    except OSError:
        print(f"[*] {target_ip} hittades inte på denna dator. Fallback till 127.0.0.1 (localhost).")
        return '127.0.0.1'

# Sätter HOST till 10.0.0.1 om den finns, annars 127.0.0.1
HOST = get_valid_host(DESIRED_HOST)
# ------------------------------------

# --- MELLANSLAGS-LYSSNARE ---
def send_local_toggle():
    """Skapar en tillfällig klient som skickar 'TOGGLE' till din egen server."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT)) # Använder nu den verifierade HOST:en
        client_socket.sendall(b'TOGGLE')
        client_socket.close()
    except Exception as e:
        print(f"\n[!] Manuellt avbrott misslyckades: {e}")

def listen_for_spacebar():
    """Lyssnar i bakgrunden efter mellanslag och triggar send_local_toggle."""
    keyboard.add_hotkey('space', send_local_toggle)
    keyboard.wait()

listener_thread = threading.Thread(target=listen_for_spacebar, daemon=True)
listener_thread.start()
# -----------------------------

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    print(f"Lyssnar efter knapptryck på {HOST}:{PORT}... (Tryck SPACE för att manuellt toggla)")

    is_recording = False
    emotion_process = None
    audio_process = None
    audio_file = "current_recording.mp3"
    
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