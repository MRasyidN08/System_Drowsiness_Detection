import cv2
import time
from datetime import datetime
from ultralytics import YOLO
import RPi.GPIO as GPIO
import BlynkLib
from flask import Flask, Response
import threading

# === BLYNK SETUP ===
BLYNK_AUTH_TOKEN = 'JMSJoJYzqTPfOYA6P3ywfot82MfIySRt'
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN)

# Virtual Pins
VPIN_LED = 1
VPIN_STATUS = 2
VPIN_TERMINAL = 3
VPIN_FAULT = 4

# === GPIO SETUP ===
GPIO.setmode(GPIO.BCM)
RED_LED = 17
BUZZER = 25
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.output(RED_LED, GPIO.LOW)
GPIO.output(BUZZER, GPIO.LOW)

# === YOLO SETUP ===
model = YOLO("/home/klp6/Downloads/best(1).pt")
print(model.names)
TARGET_LABEL = "drowsy"

# === FLASK SETUP ===
app = Flask(_name_)
drowsy_count = 0

@app.route('/')
def index():
    return f'''
        <html>
        <head>
            <title>Sistem Deteksi Kantuk</title>
            <style>
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(to right, #e0f7fa, #ffffff);
                    padding: 20px;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: auto;
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);
                }}
                .log-box, .stats-box {{
                    background-color: #f5f5f5;
                    border: 1px solid #ccc;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 15px;
                }}
                pre {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    height: 200px;
                    overflow-y: scroll;
                    background-color: #212121;
                    color: #00e676;
                    padding: 10px;
                    border-radius: 5px;
                }}
                img {{
                    border-radius: 8px;
                    border: 1px solid #ccc;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Sistem Deteksi Kantuk</h1>
                <img src="/video" width="640" height="480"><br><br>

                <div class="stats-box">
                    <h3>Statistik Deteksi</h3>
                    <p>Total Deteksi Mengantuk: <span id="count">0</span></p>
                </div>

                <div class="log-box">
                    <h3>Log Deteksi</h3>
                    <pre id="log">Memuat log...</pre>
                </div>
            </div>

            <script>
                function fetchLog() {{
                    fetch('/log')
                        .then(response => response.text())
                        .then(data => {{
                            const logBox = document.getElementById("log");
                            logBox.textContent = data;
                            logBox.scrollTop = logBox.scrollHeight;
                        }});
                }}

                function fetchStats() {{
                    fetch('/stats')
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById("count").textContent = data.total_drowsy;
                        }});
                }}

                setInterval(() => {{
                    fetchLog();
                    fetchStats();
                }}, 3000);

                fetchLog();
                fetchStats();
            </script>
        </body>
        </html>
    '''

@app.route('/video')
def video():
    def generate_frames():
        while True:
            success, frame = camera.read()
            if not success:
                continue
            frame = detect_drowsiness(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/log')
def get_log():
    try:
        with open("drowsiness_log.txt", "r") as f:
            content = f.read()
        return Response(content, mimetype='text/plain')
    except FileNotFoundError:
        return Response("Log belum tersedia.", mimetype='text/plain')

@app.route('/stats')
def stats():
    return {'total_drowsy': drowsy_count}

def run_flask():
    app.run(host='0.0.0.0', port=5000)

flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# === CAMERA SETUP ===
def try_open_camera(index):
    cap = cv2.VideoCapture(index)
    if cap.isOpened():
        print(f"[INFO] Kamera {index} berhasil dibuka.")
        return cap
    print(f"[WARN] Kamera {index} gagal dibuka.")
    return None

def open_first_available_camera():
    for i in range(10):
        cam = try_open_camera(i)
        if cam:
            return cam
    return None

camera = open_first_available_camera()
if camera is None:
    print("[ERROR] Tidak ada kamera yang tersedia.")
    GPIO.cleanup()
    exit(1)

# === DETEKSI KANTUK ===
def detect_drowsiness(frame):
    global drowsy_count, drowsy_start_time
    blynk.run()
    results = model(frame)
    names = model.names
    detected_drowsy = False

    for result in results:
        blynk.run()
        for box in result.boxes:
            cls_id = int(box.cls[0])
            label = names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            color = (0, 0, 255) if label == TARGET_LABEL else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if label == TARGET_LABEL:
                detected_drowsy = True

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp, (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    print(f"[{timestamp}] Frame diproses. Drowsy terdeteksi: {detected_drowsy}")
    blynk.run()

    current_time = time.time()

    if detected_drowsy:
        if drowsy_start_time is None:
            drowsy_start_time = current_time
        elif current_time - drowsy_start_time >= 1.5:
            # Sudah mengantuk selama 1.5 detik
            GPIO.output(RED_LED, GPIO.HIGH)
            GPIO.output(BUZZER, GPIO.HIGH)
            blynk.virtual_write(VPIN_LED, 1)
            blynk.virtual_write(VPIN_STATUS, "drowsy")
            blynk.virtual_write(VPIN_TERMINAL, f"[{timestamp}] Status: DROWSY")
            blynk.virtual_write(VPIN_FAULT, f"Status Fault Tidak Ditemukan")
            with open("drowsiness_log.txt", "a") as f:
                f.write(f"[{timestamp}] DROWSY terdeteksi\n")
            drowsy_count += 1
    else:
        drowsy_start_time = None
        GPIO.output(RED_LED, GPIO.LOW)
        GPIO.output(BUZZER, GPIO.LOW)
        blynk.virtual_write(VPIN_LED, 0)
        blynk.virtual_write(VPIN_STATUS, "normal")

    blynk.run()
    return frame

# === MAIN LOOP (DENGAN AUTO-RECONNECT CAMERA) ===
try:
    while True:
        blynk.run()
        success, frame = camera.read()
        if not success:
            print("[WARN] Gagal membaca frame. Mencoba kamera lain...")
            camera.release()
            camera = open_first_available_camera()
            if camera is None:
                print("[ERROR] Tidak ada kamera aktif. Menunggu 5 detik lalu coba lagi...")
                time.sleep(5)
                continue
            else:
                print("[INFO] Kamera berhasil disambungkan ulang.")
                continue

        frame = detect_drowsiness(frame)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[INFO] Dihentikan oleh pengguna.")

finally:
    if camera:
        camera.release()
    GPIO.output(RED_LED, GPIO.LOW)
    GPIO.output(BUZZER, GPIO.LOW)
    GPIO.cleanup()
    print("[INFO] Program selesai dan GPIO dibersihkan.")