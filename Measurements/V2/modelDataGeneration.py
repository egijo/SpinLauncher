import cv2
import numpy as np
import os
import sys

# ==========================================================
# PARAMETER
# ==========================================================
VIDEO_PATH = "Videos/23_40_9.mp4"
OUTPUT_DIR = "puckData/150x150"
PATCH_SIZE = 150

# ==========================================================
# VORBEREITUNG
# ==========================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("FEHLER: Video konnte nicht geöffnet werden")
    sys.exit(1)

patch_counter = 176
selected_center = None

# ==========================================================
# MAUS-CALLBACK
# ==========================================================
def mouse_callback(event, x, y, flags, param):
    global selected_center
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_center = (x, y)

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", mouse_callback)

# ==========================================================
# HAUPTSCHLEIFE
# ==========================================================
frame_idx = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Video zu Ende.")
        break

    # Schwarz-Weiß sicherstellen
    if frame.ndim == 3:
        gray = frame[:, :, 0]
    else:
        gray = frame

    vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    h, w = gray.shape

    while True:
        display = vis.copy()

        if selected_center is not None:
            cx, cy = selected_center
            x1 = cx - PATCH_SIZE // 2
            y1 = cy - PATCH_SIZE // 2
            x2 = x1 + PATCH_SIZE
            y2 = y1 + PATCH_SIZE

            # Begrenzen auf Bild
            x1 = max(0, min(x1, w - PATCH_SIZE))
            y1 = max(0, min(y1, h - PATCH_SIZE))
            x2 = x1 + PATCH_SIZE
            y2 = y1 + PATCH_SIZE

            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.putText(
            display,
            f"Frame {frame_idx} | Klick = Position | ENTER = speichern | n = skip | ESC = Ende",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow("Frame", display)
        key = cv2.waitKey(20) & 0xFF

        # ENTER → Patch speichern
        if key == 13 and selected_center is not None:
            cx, cy = selected_center
            x1 = cx - PATCH_SIZE // 2
            y1 = cy - PATCH_SIZE // 2

            x1 = max(0, min(x1, w - PATCH_SIZE))
            y1 = max(0, min(y1, h - PATCH_SIZE))

            patch = gray[y1:y1 + PATCH_SIZE, x1:x1 + PATCH_SIZE]

            fname = os.path.join(
                OUTPUT_DIR,
                f"patch_{patch_counter:06d}.png"
            )
            cv2.imwrite(fname, patch)
            print(f"Gespeichert: {fname}")

            patch_counter += 1
            selected_center = None
            break

        # n → Frame überspringen
        elif key == ord('n'):
            selected_center = None
            break

        # ESC → Abbruch
        elif key == 27:
            cap.release()
            cv2.destroyAllWindows()
            print("Abbruch durch Benutzer")
            sys.exit(0)

    frame_idx += 1

# ==========================================================
# AUFRÄUMEN
# ==========================================================
cap.release()
cv2.destroyAllWindows()
print(f"\nFertig. Gespeicherte Patches: {patch_counter}")
