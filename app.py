from flask import Flask, jsonify, request
import threading
import os
import time
import random
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Admin API Key (change this to something secret)
ADMIN_API_KEY = "my_secret_admin_key"

# Global state
count = 0.0
max_rising_value = 0.0
phase = "idle"
thread_started = False
thread_lock = threading.Lock()
custom_rising_value = None
rising_start_value = 0.0
rising_max_value = 50.0
period = 0
past_periods = []

def run_counter():
    global count, phase, max_rising_value, custom_rising_value, period, past_periods, rising_start_value, rising_max_value

    while True:
        # Phase 1: Countdown
        count = 15
        phase = "countdown"
        for _ in range(15):
            time.sleep(1)
            count -= 1

        # Phase 2: Rising
        count = rising_start_value
        phase = "rising"
        max_target = custom_rising_value if custom_rising_value is not None else rising_max_value
        while count < max_target:
            time.sleep(0.2)
            count += random.uniform(0.1, 1.0)
            count = min(round(count, 2), max_target)
            if custom_rising_value is None and (count >= max_target or random.random() < 0.03):
                break

        max_rising_value = round(count, 2)
        timestamp = datetime.now().strftime('%y-%m-%d %H:%M:%S')
        past_periods.append({"end": str(max_rising_value), "time": timestamp})
        period += 1

        print(f"Simulated Firebase push: {max_rising_value} at {timestamp}")

        custom_rising_value = None
        phase = "complete"
        time.sleep(3)
        phase = "idle"

@app.route('/start')
def get_status():
    global thread_started
    with thread_lock:
        if not thread_started:
            thread_started = True
            threading.Thread(target=run_counter, daemon=True).start()

    response = {
        "phase": phase,
        "count": round(count, 2),
        "period": period,
        "past_periods": past_periods
    }
    if phase == " complete":
        response[" complete"] = max_rising_value
    return jsonify(response)

@app.route('/set_value', methods=['POST'])
def set_custom_value():
    global custom_rising_value

    if phase != "countdown":
        return jsonify({"error": f"Cannot set value during '{phase}' phase. Wait for countdown."}), 400

    data = request.get_json()
    value = data.get("value")
    if isinstance(value, (int, float)) and 0 <= value <= 100:
        custom_rising_value = round(value, 2)
        return jsonify({"status": "custom rising value scheduled", "value": custom_rising_value}), 200
    return jsonify({"error": "Invalid value"}), 400

@app.route('/admin/set_config', methods=['POST'])
def admin_set_config():
    global rising_start_value, rising_max_value, period

    api_key = request.headers.get("X-API-Key")
    if api_key != ADMIN_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    start = data.get("rising_start")
    max_val = data.get("rising_max")
    start_period = data.get("start_period")

    if isinstance(start, (int, float)) and 0 <= start <= 100:
        rising_start_value = round(start, 2)
    else:
        return jsonify({"error": "Invalid rising_start value"}), 400

    if isinstance(max_val, (int, float)) and start < max_val <= 100:
        rising_max_value = round(max_val, 2)
    else:
        return jsonify({"error": "Invalid rising_max value"}), 400

    if isinstance(start_period, int) and start_period >= 0:
        period = start_period

    return jsonify({
        "status": "config updated",
        "rising_start_value": rising_start_value,
        "rising_max_value": rising_max_value,
        "period": period
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # <- fixed closing parenthesi