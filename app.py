from flask import Flask, jsonify
import threading, time, random, firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os, base64, tempfile

# Flask app setup
app = Flask(__name__)

# Firebase setup
encoded = os.environ.get("FIREBASE_CREDENTIALS_BASE64")
decoded_json = base64.b64decode(encoded).decode("utf-8")
with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as f:
    f.write(decoded_json)
    temp_path = f.name

cred = credentials.Certificate(temp_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sk-diondstore-default-rtdb.firebaseio.com'
})

# Shared state
count = 0.0
max_rising_value = 0.0
phase = "idle"
lock = threading.Lock()
running = False

def run_cycle():
    global count, max_rising_value, phase, running

    while True:
        with lock:
            if running:
                continue
            running = True
            count = 15
            phase = "countdown"

        # Countdown from 15 to 0
        while count > 0:
            time.sleep(1)
            with lock:
                count -= 1

        with lock:
            count = 0.0
            phase = "rising"

        # Rising phase
        while True:
            time.sleep(0.2)
            with lock:
                count += random.uniform(0.1, 1.0)
                count = round(count, 2)
                if count >= 50 or random.random() < 0.03:
                    break

        with lock:
            max_rising_value = count
            phase = "done"
            db.reference("his/Value").set(max_rising_value)

        time.sleep(3)
        with lock:
            phase = "idle"
            running = False

@app.route('/start')
def start_or_status():
    with lock:
        if not running and phase in ["idle", "done"]:
            threading.Thread(target=run_cycle, daemon=True).start()
        return jsonify({
            "phase": phase,
            "count": round(count, 2),
            "done": max_rising_value if phase == "done" else None
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
