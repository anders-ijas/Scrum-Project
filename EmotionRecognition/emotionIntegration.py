import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time
import os

os.environ["GOOGLE_CLOUD_FIRESTORE_FORCE_REST"] = "true"
os.environ["GRPC_DNS_RESOLVER"] = "native"

class FirebaseLogger:
    def __init__(self, key_path):
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.last_upload_time = 0
        self.last_emotion = None
        self.session_id = None  # Tracks the browser session ID[cite: 13]
    
    def get_active_session_id(self):
        """
        Fetches the sessionID written by the frontend to the 'current' document[cite: 2, 13].
        """
        try:
            doc = self.db.collection("emotion").document("current").get()
            if doc.exists:
                data = doc.to_dict()
                self.session_id = data.get("sessionID")
                print(f"🔗 Synced with SessionID: {self.session_id}")
            else:
                print("⚠️ 'current' document not found. SessionID remain None.")
        except Exception as e:
            print(f"❌ Failed to fetch sessionID: {e}")

    def sync_conversation_start(self, output_data):
        """
        Sends all exchanges (question/answer pairs) to Firebase[cite: 13].
        """
        try:
            exchanges = output_data.get("exchanges", [])
            
            for i, exchange in enumerate(exchanges):
                question_obj = exchange.get("question", {})
                answer_obj = exchange.get("answer", {})
                
                line1 = question_obj.get("text", "") if question_obj else ""
                line2 = answer_obj.get("text", "") if answer_obj else ""
                answer_timestamp = answer_obj.get("startMs") if answer_obj else None

                update_data = {
                    "question": str(line1),
                    "answer": str(line2),
                    "answerTimestampMs": answer_timestamp
                }
                
                self.db.collection("emotion").document("current").update(update_data)
                print(f"✅ Synced exchange {i + 1}: Question='{line1}', Answer='{line2}'")
                
                time.sleep(0.5)
                
        except Exception as e:
            print(f"❌ Firebase Transcription Sync Failed: {e}")
    
    def archive_emotion_change(self, emotion, accuracy, emotion_timestamp):
        """
        Archives the emotion change with the linked sessionID and the provided timestamp[cite: 13].
        """
        # Ensure we have the sessionID before archiving
        if not self.session_id:
            self.get_active_session_id()

        archive_data = {
            "emotion": str(emotion),
            "accuracy": str(round(float(accuracy) * 100, 2)),
            "emotionTimestamp": emotion_timestamp, # Uses timestamp from EmotionalRecognition.py[cite: 13, 14]
            "sessionID": self.session_id,           # Links archive to the specific web session[cite: 13]
            "archived": True
        }
        try:
            self.db.collection("emotion").add(archive_data)
            print(f"📦 Archived emotion change: {archive_data}")
        except Exception as e:
            print(f"❌ Emotion archive failed: {e}")
    
    def update_current_emotion(self, label, score, emotion_timestamp=None, color_bgr=None):
        current_time = time.time()
        emotion_str = str(label)
        accuracy_str = str(round(float(score) * 100, 2))
        color_bgr_data = [int(value) for value in color_bgr] if color_bgr is not None else None

        if self.last_emotion is None:
            self.last_emotion = emotion_str

        # Archive only when emotion changes
        if emotion_str != self.last_emotion:
            # Passes the provided timestamp through to the archive[cite: 13, 14]
            self.archive_emotion_change(emotion_str, score, emotion_timestamp)
            self.last_emotion = emotion_str
        
        if current_time - self.last_upload_time > 1.1:
            try:
                doc_data = {
                    "emotion": emotion_str,
                    "accuracy": accuracy_str,
                    "question": "",
                    "answer": "",
                    "emotionTimestamp": emotion_timestamp, # Keeps 'current' in sync with recognition[cite: 1, 13]
                    "last_updated": datetime.datetime.now(datetime.timezone.utc)
                }
                if color_bgr_data is not None:
                    doc_data["colorBgr"] = color_bgr_data
                
                self.db.collection("emotion").document("current").update(doc_data)
                
                self.last_upload_time = current_time
                print(f"✅ Sync Success: {emotion_str} ({accuracy_str}%)")
            except Exception as e:
                print(f"❌ Sync Error: {e}")
