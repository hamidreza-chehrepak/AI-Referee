import cv2
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Camera not found!")
        break

    results = model.track(frame, persist=True, classes=[0], verbose=False)

    person_count = len(results[0].boxes)

    annotated_frame = results[0].plot()

    cv2.putText(
        annotated_frame,
        f"Persons: {person_count}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("AI Referee - YOLO", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()