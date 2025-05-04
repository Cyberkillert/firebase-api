from flask import Flask, jsonify
from flask_socketio import SocketIO
import threading
import os
import time
import random
import firebase_admin
from firebase_admin import credentials, db
import base64
import tempfile

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # WebSocket support

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

# Background thread flag
thread_started = False
thread_lock = threading.Lock()

def run_counter():
    global count, phase, max_rising_value

    while True:
        count = 15
        phase = "countdown"
        while count > 0:
            socketio.emit("update", {"countdown": round(count, 2)})
            time.sleep(1)
            count -= 1

        count = 0.0
        phase = "rising"
        while count < 50.0:
            socketio.emit("update", {"rising": round(count, 2)})
            time.sleep(0.2)
            count += random.uniform(0.1, 1.0)
            count = round(count, 2)
            if count >= 50 or random.random() < 0.03:
                break

        max_rising_value = round(count, 2)

        # Push to Firebase
        db.reference("his/Value").set(max_rising_value)

        phase = "done"
        socketio.emit("update", {"done": max_rising_value})

        time.sleep(3)
        phase = "idle"

@app.route('/start')
def get_status():
    global thread_started

    with thread_lock:
        if not thread_started:
            thread_started = True
            threading.Thread(target=run_counter, daemon=True).start()

    if phase == "done":
        return jsonify({"done": max_rising_value})
    else:
        return jsonify({phase: round(count, 2)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
