import cv2
import mediapipe as mp
import os
import time
import math
from collections import deque

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = "models/hand_landmarker.task"

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2,
)

landmarker = HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

os.makedirs("screenshots", exist_ok=True)

last_save_time = 0
image_number = 0

# نگهداری نتیجه 7 فریم اخیر برای هر دست
history = {
    0: deque(maxlen=7),
    1: deque(maxlen=7),
}


def angle(a, b, c):
    ba = (a.x - b.x, a.y - b.y)
    bc = (c.x - b.x, c.y - b.y)

    dot = ba[0] * bc[0] + ba[1] * bc[1]

    mag_ba = math.hypot(ba[0], ba[1])
    mag_bc = math.hypot(bc[0], bc[1])

    if mag_ba == 0 or mag_bc == 0:
        return 0

    value = dot / (mag_ba * mag_bc)
    value = max(-1.0, min(1.0, value))

    return math.degrees(math.acos(value))


def detect_fingers(hand):
    """
    خروجی:
    [Thumb, Index, Middle, Ring, Pinky]
    """

    # چهار انگشت اصلی:
    # MCP -> PIP -> DIP -> TIP

    fingers = []

    finger_points = [
        (5, 6, 7, 8),      # Index
        (9, 10, 11, 12),   # Middle
        (13, 14, 15, 16),  # Ring
        (17, 18, 19, 20),  # Pinky
    ]

    for mcp, pip, dip, tip in finger_points:

        pip_angle = angle(
            hand[mcp],
            hand[pip],
            hand[dip]
        )

        dip_angle = angle(
            hand[pip],
            hand[dip],
            hand[tip]
        )

        # انگشت باز معمولاً مفاصل نسبتاً صاف دارد
        is_open = (
            pip_angle > 150 and
            dip_angle > 150
        )

        fingers.append(is_open)

    # شست
    thumb_ip_angle = angle(
        hand[2],
        hand[3],
        hand[4]
    )

    # فاصله نوک شست از MCP اشاره
    thumb_spread = math.hypot(
        hand[4].x - hand[5].x,
        hand[4].y - hand[5].y
    )

    palm_width = math.hypot(
        hand[5].x - hand[17].x,
        hand[5].y - hand[17].y
    )

    thumb_open = (
        thumb_ip_angle > 150 and
        thumb_spread > palm_width * 0.7
    )

    # ترتیب نهایی:
    # Thumb, Index, Middle, Ring, Pinky

    return [
        thumb_open,
        fingers[0],
        fingers[1],
        fingers[2],
        fingers[3],
    ]


def stabilize(hand_id, current_state):
    """
    نتیجه 7 فریم اخیر را بررسی می‌کند.
    اگر حداقل 4 فریم یک وضعیت را داشته باشند،
    همان وضعیت نهایی می‌شود.
    """

    history[hand_id].append(current_state)

    if len(history[hand_id]) < 3:
        return current_state

    result = []

    for finger_index in range(5):

        votes = sum(
            frame[finger_index]
            for frame in history[hand_id]
        )

        result.append(
            votes >= len(history[hand_id]) / 2
        )

    return result


while True:

    ret, frame = cap.read()

    if not ret:
        print("Camera not found!")
        break

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    result = landmarker.detect(mp_image)

    if result.hand_landmarks:

        for hand_id, hand in enumerate(
            result.hand_landmarks
        ):

            if hand_id not in history:
                history[hand_id] = deque(maxlen=7)

            raw_state = detect_fingers(hand)

            fingers = stabilize(
                hand_id,
                raw_state
            )

            open_count = sum(fingers)

            names = [
                "Thumb",
                "Index",
                "Middle",
                "Ring",
                "Pinky"
            ]

            print(f"\nHand {hand_id + 1}")

            for name, state in zip(
                names,
                fingers
            ):

                status = "OPEN" if state else "CLOSED"

                print(
                    f"{name}: {status}"
                )

            print(
                f"Total OPEN: {open_count}"
            )

            # رسم نقاط
            for landmark in hand:

                x = int(
                    landmark.x *
                    frame.shape[1]
                )

                y = int(
                    landmark.y *
                    frame.shape[0]
                )

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

            # نمایش نتیجه
            cv2.putText(
                frame,
                f"Hand {hand_id + 1}: {open_count} OPEN",
                (30, 50 + hand_id * 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    # ذخیره عکس هر 2 ثانیه
    current_time = time.time()

    if current_time - last_save_time >= 2:

        image_number += 1

        filename = (
            f"screenshots/"
            f"hand_{image_number:03d}.jpg"
        )

        cv2.imwrite(
            filename,
            frame
        )

        print(f"Saved: {filename}")

        last_save_time = current_time

    cv2.imshow(
        "AI Referee - Finger Detection",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
landmarker.close()
cv2.destroyAllWindows()