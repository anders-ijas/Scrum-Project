import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time
import os
# These MUST be set before you import firebase_admin
os.environ["GOOGLE_CLOUD_FIRESTORE_FORCE_REST"] = "true"
os.environ["GRPC_DNS_RESOLVER"] = "native"  # Force standard network behavior to prevent hanging on Linux
# FORCE standard network behavior (fixes the 'hanging' on Linux)

class FirebaseLogger:
    def __init__(self, key_path):
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        
        # Initialize Firestore
        self.db = firestore.client()
        self.last_upload_time = 0
    def sync_conversation_start(self, output_data):
        """
        Takes the first two segments and maps them to question/answer fields.
        """
        try:
            segments = output_data.get("segments", [])
            
            # Extract only the first two lines
            line1 = segments[0]["text"] if len(segments) > 0 else ""
            line2 = segments[1]["text"] if len(segments) > 1 else ""

            update_data = {
                "question": str(line1),
                "answer": str(line2),
                "last_updated": datetime.datetime.now(datetime.timezone.utc)
            }
            
            # Use .update() so we don't delete the emotion/accuracy data
            self.db.collection("emotion").document("current").update(update_data)
            print(f"✅ Firebase: Syncing conversation snippet: Q: {line1[:20]}... A: {line2[:20]}...")
            
        except Exception as e:
            print(f"❌ Firebase Transcription Sync Failed: {e}")
    def update_current_emotion(self, label, score):
        current_time = time.time()
        
        # Strictly enforce the 1-second rule to prevent network backup
        if current_time - self.last_upload_time > 1.1:
            try:
                # Ensure fields match EXACTLY what util.js extracts
                doc_data = {
                    "emotion": str(label), 
                    "accuracy": str(round(float(score) * 100, 2)), # Needs to be String for .trim()
                    "question": "",  # Included so util.js doesn't get 'undefined'
                    "answer": "",    # Included so util.js doesn't get 'undefined'
                    "last_updated": datetime.datetime.now(datetime.timezone.utc)
                }
                
                # Match the collection 'emotion' and doc 'current'
                self.db.collection("emotion").document("current").set(doc_data)
                
                self.last_upload_time = current_time
                print(f"✅ Sync Success: {label} ({doc_data['accuracy']}%)")
            except Exception as e:
                print(f"❌ Sync Error: {e}")