import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

class FirebaseLogger:
    def __init__(self, key_path):
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.last_upload_time = 0

    def update_current_emotion(self, label, score):
        """Updates Firestore only if 1 second has passed since the last update."""
        current_time = time.time()
        
        if current_time - self.last_upload_time > 1.0:
            try:
                doc_data = {
                    "emotion": str(label),
                    "accuracy": round(float(score) * 100, 2),
                    "last_updated": datetime.datetime.now(datetime.timezone.utc)
                }
                self.db.collection("emotion_data").document("current").set(doc_data)
                self.last_upload_time = current_time
            except Exception as e:
                print(f"Firestore Sync Failed: {e}")