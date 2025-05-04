from flask import Flask, jsonify
import threading
import os
import time
import random
import firebase_admin
from firebase_admin import credentials, db
import base64
import tempfile
from datetime import datetime

app = Flask(__name__)

# Firebase Admin SDK setup from base64-encoded env var
encoded = os.environ.get("FIREBASE_CREDENTIALS_BASE64")
decoded_json = base64.b64decode(encoded).decode("utf-8")

# Write decoded credentials to a temporary file
with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as f:
    f.write(decoded_json)
    temp_path = f.name

# Initialize Firebase
cred = credentials.Certificate(temp_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sk-diondstore-default-rtdb.firebaseio.com'
})

# Global variables
count = 0.0
max_rising_value = 0.0
phase = "idle"
thread_started = False
thread_lock = threading.Lock()

# Keep last 50 results
def push_to_firebase(value):
    now = datetime.utcnow().strftime("%y%m%d%H%M%S")
    ref = db.reference("his")
    ref.set({
        now: {
            "Ended. Max": value,
            "time": now
        }
    })

    # Keep only latest 50 entries
    all_data = ref.get()
    if all_data and len(all_data) > 50:
        sorted_keys = sorted(all_data.keys())
        for key in sorted_keys[:-50]:
            ref.child(key).delete()

def run_counter():
    global count, phase, max_rising_value

    while True:
        # Countdown phase
        count = 15
        phase = "countdown"
        while count > 0:
            time.sleep(1)
            count -= 1

        # Rising phase (with timeout limit to prevent infinite loop)
        count = 0.0
        phase = "rising"
        start_time = time.time()
        max_duration = 15  # seconds

        while True:
            count += random.uniform(0.5, 1.2)
            count = round(count, 2)

            if count >= 50.0 or time.time() - start_time > max_duration:
                break

            time.sleep(0.2)

        max_rising_value = count
        phase = "done"

        # Push to Firebase
        push_to_firebase(max_rising_value)

        # Wait and reset
        time.sleep(3)
        phase = "idle"

@app.route('/start')
def get_status():
    global thread_started

    with thread_lock:
        if not thread_started:
            thread_started = True
            threading.Thread(target=run_counter, daemon=True).start()

    return jsonify({
        "phase": phase,
        "count": round(count, 2)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
