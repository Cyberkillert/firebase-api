from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import threading, time, random, firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os, base64, tempfile

# Initialize Flask app
app = Flask(__name__)

# Firebase setup from env var
encoded = os.environ.get("FIREBASE_CREDENTIALS_BASE64")
decoded_json = base64.b64decode(encoded).decode("utf-8")
with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as f:
    f.write(decoded_json)
    temp_path = f.name

cred = credentials.Certificate(temp_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sk-diondstore-default-rtdb.firebaseio.com'
})

# Global variables
count = 0.0
max_rising_value = 0.0
phase = "idle"

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

        # Mark end of rising phase
        max_rising_value = round(count, 2)

        # Push value to Firebase under "his/Value"
        ref = db.reference("his/Value")
        ref.set(max_rising_value)

        phase = "done"

        # Optional delay before restarting
        time.sleep(3)
        phase = "idle"

# Start the counter thread immediately
threading.Thread(target=run_counter, daemon=True).start()

@app.route('/start')
def get_status():
    global phase, count, max_rising_value

    if phase == "done":
        return jsonify({"done": max_rising_value})
    else:
        return jsonify({phase: round(count, 2)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    
