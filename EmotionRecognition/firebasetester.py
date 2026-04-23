import time
from emotionIntegration import FirebaseLogger

key_path = "../integration/service-account.json" 

try:
    logger = FirebaseLogger(key_path)
    print("✅ Firebase initialized successfully.")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    exit()

# 2. THE TEST LOOP
print("\nStarting mock upload test...")
test_data = [
    ("Glad", 0.99),
    ("sadness", 0.45),
    ("neutral", 0.88)
]

for emotion, score in test_data:
    print(f"Sending: {emotion} with {score} accuracy...")
    
    # This calls your function in firebase_handler.py
    logger.update_current_emotion(emotion, score)
    
    # Wait 1.1 seconds to stay within the 1-write-per-second limit
    time.sleep(1.1)

print("\nAll test data sent! Check your Firestore console.")