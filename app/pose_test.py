import cv2
import os
import time
from ultralytics import YOLO

model = YOLO("yolo11n-pose.pt")

cap = cv2.VideoCapture(0)

os.makedirs("screenshots", exist_ok=True)

last_save_time = 0
image_number = 0

while True:
    ret, frame = cap.read()

    if not ret:
        print("Camera not found!")
        break

    results = model.track(
        frame,
        persist=True,
        classes=[0],
        verbose=False
    )

    annotated_frame = results[0].plot()

    # هر ۲ ثانیه یک عکس ذخیره کن
    current_time = time.time()

    if current_time - last_save_time >= 2:
        image_number += 1

        filename = f"screenshots/frame_{image_number:03d}.jpg"

        cv2.imwrite(filename, annotated_frame)

        print(f"Saved: {filename}")

        last_save_time = current_time

    cv2.imshow("AI Referee - Pose", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()