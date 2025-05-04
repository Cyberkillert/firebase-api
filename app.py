from flask import Flask, jsonify
import threading, time, random, firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os, base64, tempfile

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

def run_cycle_forever():
    global count, max_rising_value, phase

    while True:
        # Countdown Phase
        with lock:
            count = 15
            phase = "countdown"
        while count > 0:
            time.sleep(1)
            with lock:
                count -= 1

        # Rising Phase
        with lock:
            count = 0.0
            phase = "rising"
        while True:
            time.sleep(0.2)
            with lock:
                count += random.uniform(0.1, 1.0)
                count = round(count, 2)
                if count >= 50 or random.random() < 0.03:
                    break

        # Done Phase
        with lock:
            max_rising_value = count
            phase = "done"

            timestamp = datetime.utcnow().strftime("%y%m%d%H%M%S")
            ref = db.reference("his")
            ref.child("Value").set({
                "Ended. Max": max_rising_value,
                "time": timestamp
            })
            history_ref = ref.child("history")
            history_ref.push({
                "value": max_rising_value,
                "time": timestamp
            })

            # Keep only last 50 entries
            history = history_ref.get()
            if history and len(history) > 50:
                keys = list(history.keys())[:-50]
                for key in keys:
                    history_ref.child(key).delete()

        # Wait before restarting the next round
        time.sleep(3)
        with lock:
            phase = "idle"

@app.route('/start')
def get_status():
    with lock:
        response = {
            "phase": phase,
            "count": round(count, 2)
        }
        if phase == "done":
            response["done"] = max_rising_value
        return jsonify(response)

if __name__ == '__main__':
    threading.Thread(target=run_cycle_forever, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
