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
        
        self.db = firestore.client()
        self.last_upload_time = 0
    
    def sync_conversation_start(self, output_data):
        """
        Sends all exchanges (question/answer pairs) to Firebase, with a small sleep between each pair.
        """
        try:
            exchanges = output_data.get("exchanges", [])
            
            # Process each exchange (already paired as question/answer)
            for i, exchange in enumerate(exchanges):
                question_obj = exchange.get("question", {})
                answer_obj = exchange.get("answer", {})
                
                line1 = question_obj.get("text", "") if question_obj else ""
                line2 = answer_obj.get("text", "") if answer_obj else ""

                update_data = {
                    "question": str(line1),
                    "answer": str(line2),
                    "last_updated": datetime.datetime.now(datetime.timezone.utc)
                }
                
                self.db.collection("emotion").document("current").update(update_data)
                print(f"✅ Synced exchange {i + 1}: Question='{line1}', Answer='{line2}'")
                
                # Small sleep between updates
                time.sleep(0.5)
                
        except Exception as e:
            print(f"❌ Firebase Transcription Sync Failed: {e}")
    
    def update_current_emotion(self, label, score):
        current_time = time.time()
        
        if current_time - self.last_upload_time > 1.1:
            try:
                doc_data = {
                    "emotion": str(label), 
                    "accuracy": str(round(float(score) * 100, 2)), # Needs to be String for .trim()
                    "question": "",  # Included so util.js doesn't get 'undefined'
                    "answer": "",    # Included so util.js doesn't get 'undefined'
                    "last_updated": datetime.datetime.now(datetime.timezone.utc)
                }
                
                self.db.collection("emotion").document("current").update(doc_data)
                
                self.last_upload_time = current_time
                print(f"✅ Sync Success: {label} ({doc_data['accuracy']}%)")
            except Exception as e:
                print(f"❌ Sync Error: {e}")