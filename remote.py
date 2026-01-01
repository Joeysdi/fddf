# remote.py
from flask import Flask, Response, render_template_string, request
import mss
import cv2
import numpy as np
import pyautogui
import threading
import socket
from constants import PASSWORD, PRIMARY_MONITOR, JPEG_QUALITY, FLASK_HOST, FLASK_PORT

flask_app = Flask(__name__)

def generate_frames():
    with mss.mss() as sct:
        monitor = sct.monitors[PRIMARY_MONITOR]
        while True:
            img = sct.grab(monitor)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# [Same HTML template as original — omitted for brevity, copy from your original code]

@flask_app.route('/')
@flask_app.route('/screen')
def screen():
    if request.args.get('pass') != PASSWORD:
        return "Wrong password", 403
    # paste the full render_template_string from original here
    return render_template_string("""...full HTML...""".replace("{{PASSWORD}}", PASSWORD))

@flask_app.route('/video_feed')
def video_feed():
    if request.args.get('pass') != PASSWORD:
        return "Wrong password", 403
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@flask_app.route('/screen_click', methods=['POST'])
def screen_click():
    if request.args.get('pass') != PASSWORD:
        return "Wrong password", 403
    x = int(request.args.get('x', 0))
    y = int(request.args.get('y', 0))
    pyautogui.click(x, y)
    return "Clicked"

@flask_app.route('/type', methods=['POST'])
def type_text():
    if request.args.get('pass') != PASSWORD:
        return "Wrong password", 403
    text = request.args.get('text', '')
    pyautogui.write(text, interval=0.02)
    return "Typed"

def start_remote_server(nexus_instance):
    flask_app.nexus = nexus_instance
    threading.Thread(
        target=flask_app.run,
        kwargs={"host": FLASK_HOST, "port": FLASK_PORT, "threaded": True},
        daemon=True
    ).start()

    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except:
        local_ip = "127.0.0.1"
    nexus_instance.status.config(
        text=f"Phone remote: http://{local_ip}:{FLASK_PORT} (password: {PASSWORD})"
    )