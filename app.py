from flask import Flask, jsonify
import threading
import os
import time
import random
import firebase_admin
from firebase_admin import credentials, db
import base64
import tempfile
import datetime

# Initialize Flask app
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

def run_counter():
    global count, phase, max_rising_value

    while True:
        # Phase 1: Countdown from 15 to 0
        count = 15
        phase = "countdown"
        while count > 0:
            time.sleep(1)
            count -= 1

        # Phase 2: Random rise from 0.0 to ~50.0
        count = 0.0
        phase = "rising"
        while count < 50.0:
            time.sleep(0.2)
            count += random.uniform(0.1, 1.0)
            count = round(count, 2)
            if count >= 50 or random.random() < 0.03:
                break

        # End of rising phase
        max_rising_value = round(count, 2)

        # Get timestamp
        now = datetime.datetime.utcnow()
        compact_time = now.strftime("%y%m%d%H%M%S")

        # Push to Firebase under "his/{timestamp}"
        db.reference(f"his/{compact_time}").set({
            "Ended. Max": max_rising_value,
            "time": compact_time
        })

        # Trim to keep only latest 50
        his_ref = db.reference("his")
        entries = his_ref.get()
        if entries and len(entries) > 50:
            sorted_keys = sorted(entries.keys())
            keys_to_delete = sorted_keys[:len(entries) - 50]
            for key in keys_to_delete:
                his_ref.child(key).delete()

        # Finalize
        phase = "done"
        time.sleep(3)
        phase = "idle"

@app.route('/start')
def get_status():
    global thread_started

    # Start thread only once
    with thread_lock:
        if not thread_started:
            thread_started = True
            threading.Thread(target=run_counter, daemon=True).start()

    if phase == "done":
        return jsonify({"done": max_rising_value})
    else:
        return jsonify({phase: round(count, 2)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
