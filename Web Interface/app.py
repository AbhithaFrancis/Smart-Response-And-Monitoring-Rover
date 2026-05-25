from flask import Flask, send_file
import subprocess
import webbrowser

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('index.html')

# STREAM
@app.route('/stream')
def stream():
    url = "http://10.100.159.61/stream" 
    webbrowser.open(url)
    return "📷 Stream Started"

# HUMAN DETECTION
@app.route('/detect')
def detect():
    subprocess.Popen(["python", "human_yolo_pose.py"])
    return "🤖 Human Detection Started"

# MANUAL DRIVING
@app.route('/manual')
def manual():
    subprocess.Popen(["python", "motor_control.py"])
    return "🎮 Manual Driving Started"

if __name__ == '__main__':
    app.run(debug=True)
