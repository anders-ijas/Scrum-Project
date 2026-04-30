import socket
import subprocess
import sys
import os
import threading
import keyboard

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

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    print(f"Lyssnar efter knapptryck på {HOST}:{PORT}... (Tryck SPACE för att manuellt toggla)")

    is_recording = False
    emotion_process = None
    audio_process = None
    audio_file = "current_recording.wav" # Ändrat till .wav för din kompis script
    
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
                    
                    # --- ÄNDRING: Startar med stdin=PIPE för att kunna skicka "Enter" ---
                    audio_process = subprocess.Popen(
                        [python_path, "../EmotionRecognition/RecordAudio.py", audio_file],
                        stdin=subprocess.PIPE,
                        text=True
                    )
                    # Skickar första Enter för att börja spela in
                    audio_process.stdin.write('\n')
                    audio_process.stdin.flush()
                    
                    is_recording = True
                    
                else:
                    print("\n[-] Signal mottagen: STOPPAR processer")
                    
                    if emotion_process:
                        emotion_process.terminate()
                        emotion_process.wait() 
                        
                    if audio_process:
                        # --- ÄNDRING: Skickar andra Enter istället för terminate ---
                        print("[*] Skickar 'Enter' till inspelaren...")
                        audio_process.stdin.write('\n')
                        audio_process.stdin.flush()
                        # Väntar på att den ska spara och köra transkribering automatiskt
                        audio_process.wait()
                        
                    # --- ÄNDRING: Transkribering anropas nu av record_audio.py, så vi hoppar över den här ---
                    
                    is_recording = False
                    print("[*] Färdig. Återgår till vänteläge...")

if __name__ == "__main__":
    main()