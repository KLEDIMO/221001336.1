from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from threading import Lock

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

data_lock = Lock()
esp_data = {"analog_input": 0, "button": False, "fan_pot": 0}
control_data = {
    "led_enabled": False,
    "brightness": 0,
    "fan_enabled": False,
    "fan_speed": 0
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>IoT Dashboard</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .card { background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .status { font-size: 1.2em; margin: 10px 0; color: #333; }
        .online { color: green; }
        .offline { color: red; }
    </style>
</head>
<body>
    <h1>IoT Control Center</h1>
    <div class="dashboard">
        <div class="card">
            <h2>📊 Sensor Data</h2>
            <p class="status">🔦 Brightness: {{ esp_data.analog_input }}</p>
            <p class="status">🚨 Motion: {{ 'Detected' if esp_data.button else 'None' }}</p>
            <p class="status">🎛️ Fan Pot: {{ esp_data.fan_pot }}</p>
        </div>
        <div class="card">
            <h2>🎚️ Control Status</h2>
            <p class="status {{ 'online' if controls.led_enabled else 'offline' }}">💡 LED: {{ 'ON' if controls.led_enabled else 'OFF' }}</p>
            <p class="status">🔆 Brightness: {{ controls.brightness }}%</p>
            <p class="status {{ 'online' if controls.fan_enabled else 'offline' }}">🌀 Fan: {{ 'ON' if controls.fan_enabled else 'OFF' }}</p>
            <p class="status">🌪️ Fan Speed: {{ controls.fan_speed }}%</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, 
                               esp_data=esp_data,
                               controls=control_data)

@app.route('/esp/update', methods=['POST'])
def update_esp():
    with data_lock:
        esp_data.update(request.json)
    return jsonify({"message": "Updated"}), 200

@app.route('/esp/control')
def get_control():
    with data_lock:
        return jsonify(control_data), 200

@app.route('/flet/update', methods=['POST'])
def update_flet():
    with data_lock:
        control_data.update(request.json)
    return jsonify({"message": "Updated"}), 200

@app.route('/api/status')
def get_status():
    with data_lock:
        return jsonify({
            "sensors": esp_data,
            "controls": control_data
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)