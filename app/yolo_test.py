import cv2
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(0)

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

    result = results[0]
    annotated_frame = result.plot()

    players = []

    if result.boxes.id is not None:
        boxes = result.boxes.xyxy.cpu().tolist()
        track_ids = result.boxes.id.int().cpu().tolist()

        for box, track_id in zip(boxes, track_ids):
            x1, y1, x2, y2 = map(int, box)

            center_x = (x1 + x2) // 2

            players.append({
                "track_id": track_id,
                "center_x": center_x,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            })

    # مرتب‌سازی از چپ به راست
    players.sort(key=lambda p: p["center_x"])

    # نفر چپ = Player 2
    # نفر راست = Player 1
    for i, player in enumerate(players):

        if len(players) == 2:
            if i == 0:
                player_name = "Player 2"
            else:
                player_name = "Player 1"
        else:
            player_name = f"Player {i + 1}"

        x1 = player["x1"]
        y1 = player["y1"]
        x2 = player["x2"]

        cv2.putText(
            annotated_frame,
            player_name,
            (x1, max(y1 - 15, 30)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            3
        )

    cv2.putText(
        annotated_frame,
        f"Players: {len(players)}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        3
    )

    cv2.imshow("AI Referee - YOLO", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()