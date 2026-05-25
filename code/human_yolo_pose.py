import cv2
import time
import requests
import threading
from ultralytics import YOLO

# ================= CONFIG =================
ESP32_IP = "10.124.10.81"
STREAM_URL = "http://10.124.10.61:81/stream"
FRAME_WIDTH = 416
FRAME_HEIGHT = 320
CONF_THRESHOLD = 0.3
YOLO_SKIP = 3
SEND_COOLDOWN = 2
# ==========================================

# Pose model
model = YOLO("yolov8s-pose.pt")

cap = cv2.VideoCapture(STREAM_URL, cv2.CAP_FFMPEG)

last_state = 0
last_send_time = 0
frame_count = 0

tracked_ids = set()

def send_async(state):
    def task():
        try:
            url = f"http://{ESP32_IP}/detect?human={state}"
            requests.get(url, timeout=1)
        except:
            pass
    threading.Thread(target=task, daemon=True).start()

while True:

    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    frame_count += 1

    if frame_count % YOLO_SKIP == 0:

        results = model.track(
            frame,
            conf=CONF_THRESHOLD,
            persist=True,
            verbose=False
        )

        current_ids = set()

        for r in results:

            if r.boxes is None:
                continue

            for i, box in enumerate(r.boxes):

                if box.id is None:
                    continue

                track_id = int(box.id[0])
                current_ids.add(track_id)

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.putText(frame,f"ID:{track_id}",(x1,y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)

            # draw pose skeleton
            frame = r.plot()

        new_ids = current_ids - tracked_ids
        tracked_ids = current_ids

        detected = bool(tracked_ids)

        current_state = 1 if detected else 0
        current_time = time.time()

        if (new_ids or current_state != last_state) and \
           (current_time - last_send_time > SEND_COOLDOWN):

            send_async(current_state)
            last_send_time = current_time
            last_state = current_state

    status = "HUMAN DETECTED" if tracked_ids else "NO HUMAN"

    cv2.putText(frame,status,(20,30),
                cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0),2)

    cv2.imshow("YOLOv8 Pose Tracking",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
