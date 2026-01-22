'''import cv2
import numpy as np

# ==========================================================
# DATEI
# ==========================================================
VIDEO_PATH = "Videos/27_55_2_undistorted.mp4"

# ==========================================================
# TRACKER FACTORY (ROBUST)
# ==========================================================
def create_csrt_tracker():
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()
    elif hasattr(cv2, "legacy"):
        return cv2.legacy.TrackerCSRT_create()
    else:
        raise RuntimeError("CSRT Tracker nicht verfügbar (opencv-contrib fehlt)")

# ==========================================================
# VIDEO LADEN
# ==========================================================
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise IOError("Video konnte nicht geöffnet werden")

paused = False
tracking_active = False
roi = None
tracker = None

current_frame_gray = None

# ==========================================================
# HAUPTSCHLEIFE
# ==========================================================
while True:

    # ------------------------------------------------------
    # FRAME LESEN (nur wenn nicht pausiert ODER Tracking aktiv)
    # ------------------------------------------------------
    if not paused or tracking_active:
        ret, frame = cap.read()
        if not ret:
            break
        current_frame_gray = frame.copy()

    # Sicherstellen: Graustufen
    if len(current_frame_gray.shape) == 3:
        current_frame_gray = cv2.cvtColor(
            current_frame_gray, cv2.COLOR_BGR2GRAY
        )

    frame_bgr = cv2.cvtColor(current_frame_gray, cv2.COLOR_GRAY2BGR)

    # ------------------------------------------------------
    # TRACKING
    # ------------------------------------------------------
    if tracking_active:
        ok, bbox = tracker.update(frame_bgr)
        if ok:
            x, y, w, h = map(int, bbox)
            cx = x + w // 2
            cy = y + h // 2

            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame_bgr, (cx, cy), 4, (0, 0, 255), -1)
        else:
            cv2.putText(
                frame_bgr,
                "Tracking verloren",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

    # ------------------------------------------------------
    # INFO
    # ------------------------------------------------------
    cv2.putText(
        frame_bgr,
        "SPACE=stop | ROI ziehen | ENTER=start | ESC=Ende",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("Tracking", frame_bgr)

    key = cv2.waitKey(30) & 0xFF

    # ------------------------------------------------------
    # TASTEN
    # ------------------------------------------------------
    if key == 32 and not tracking_active:  # SPACE
        paused = True
        roi = cv2.selectROI(
            "Tracking",
            frame_bgr,
            fromCenter=False,
            showCrosshair=True
        )

    elif key == 13 and paused and roi is not None and not tracking_active:  # ENTER
        tracker = create_csrt_tracker()
        tracker.init(frame_bgr, roi)
        tracking_active = True
        paused = False

    elif key == 27:  # ESC
        break

# ==========================================================
# AUFRÄUMEN
# ==========================================================
cap.release()
cv2.destroyAllWindows()

print("Tracking beendet.")





import cv2
import numpy as np
import csv

# ==========================================================
# DATEIEN
# ==========================================================
VIDEO_PATH = "Videos/27_55_2_undistorted.mp4"
CSV_PATH   = "tracking_distance.csv"

# ==========================================================
# SCHACHBRETT
# ==========================================================
SQUARE_SIZE = 0.05      # 5 cm
MIN_CORNERS = 4
MAX_CORNERS = 12

# ==========================================================
# TRACKER FACTORY
# ==========================================================
def create_csrt_tracker():
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()
    elif hasattr(cv2, "legacy"):
        return cv2.legacy.TrackerCSRT_create()
    else:
        raise RuntimeError("CSRT Tracker nicht verfügbar")

# ==========================================================
# VIDEO LADEN
# ==========================================================
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise IOError("Video konnte nicht geöffnet werden")

paused = False
tracking_active = False
roi = None
tracker = None

frame_index = 0
start_pos = None
meter_per_pixel = None
results = []

# ==========================================================
# PIXEL → METER AUS ERSTEM FRAME
# ==========================================================
ret, first_frame = cap.read()
if not ret:
    raise RuntimeError("Erstes Frame konnte nicht gelesen werden")

gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

best_corners = None
best_pattern = None
best_count = 0

for nx in range(MIN_CORNERS, MAX_CORNERS + 1):
    for ny in range(MIN_CORNERS, MAX_CORNERS + 1):
        found, corners = cv2.findChessboardCorners(gray, (nx, ny))
        if found and nx * ny > best_count:
            best_count = nx * ny
            best_pattern = (nx, ny)
            best_corners = corners

if best_corners is None:
    raise RuntimeError("Kein Schachbrett zur Skalierung gefunden")

best_corners = cv2.cornerSubPix(
    gray, best_corners, (11, 11), (-1, -1),
    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
)

# mittlerer Abstand benachbarter Ecken (horizontal)
distances = []
for i in range(best_pattern[0] - 1):
    p1 = best_corners[i]
    p2 = best_corners[i + 1]
    distances.append(np.linalg.norm(p2 - p1))

pixel_per_square = np.mean(distances)
meter_per_pixel = SQUARE_SIZE / pixel_per_square

print(f"Skalierung: {meter_per_pixel:.6e} m / Pixel")

# ==========================================================
# VIDEO ZURÜCKSETZEN
# ==========================================================
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

current_frame_gray = None

# ==========================================================
# HAUPTSCHLEIFE
# ==========================================================
while True:

    if not paused or tracking_active:
        ret, frame = cap.read()
        if not ret:
            break
        current_frame_gray = frame.copy()

    if len(current_frame_gray.shape) == 3:
        current_frame_gray = cv2.cvtColor(
            current_frame_gray, cv2.COLOR_BGR2GRAY
        )

    frame_bgr = cv2.cvtColor(current_frame_gray, cv2.COLOR_GRAY2BGR)

    # ------------------------------------------------------
    # TRACKING
    # ------------------------------------------------------
    if tracking_active:
        ok, bbox = tracker.update(frame_bgr)
        if ok:
            x, y, w, h = map(int, bbox)
            cx = x + w // 2
            cy = y + h // 2

            if start_pos is None:
                start_pos = (cx, cy)

            dx = cx - start_pos[0]
            dy = cy - start_pos[1]
            distance_m = np.sqrt(dx**2 + dy**2) * meter_per_pixel

            results.append([frame_index, cx, cy, distance_m])

            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame_bgr, (cx, cy), 4, (0, 0, 255), -1)

            cv2.putText(
                frame_bgr,
                f"s = {distance_m:.3f} m",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2
            )

        else:
            cv2.putText(
                frame_bgr,
                "Tracking verloren",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

    # ------------------------------------------------------
    # INFO
    # ------------------------------------------------------
    cv2.putText(
        frame_bgr,
        "SPACE=stop | ROI ziehen | ENTER=start | ESC=Ende",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("Tracking", frame_bgr)

    key = cv2.waitKey(30) & 0xFF

    if key == 32 and not tracking_active:
        paused = True
        roi = cv2.selectROI("Tracking", frame_bgr, False, True)

    elif key == 13 and paused and roi is not None and not tracking_active:
        tracker = create_csrt_tracker()
        tracker.init(frame_bgr, roi)
        tracking_active = True
        paused = False

    elif key == 27:
        break

    frame_index += 1

# ==========================================================
# CSV SPEICHERN
# ==========================================================
with open(CSV_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["frame", "x_px", "y_px", "distance_m"])
    writer.writerows(results)

# ==========================================================
# AUFRÄUMEN
# ==========================================================
cap.release()
cv2.destroyAllWindows()

print("Tracking beendet.")
print("CSV gespeichert:", CSV_PATH)









import cv2
import numpy as np
import csv
import os

# ==========================================================
# DATEIEN
# ==========================================================
VIDEO_PATH = "Videos/27_55_2_undistorted.mp4"

# CSV-Pfad automatisch aus Video-Pfad ableiten
base_name = os.path.splitext(os.path.basename(VIDEO_PATH))[0]
csv_dir   = os.path.dirname(VIDEO_PATH)
CSV_PATH  = os.path.join(csv_dir, base_name + ".csv")

# ==========================================================
# ZEITBASIS
# ==========================================================
DT = 1 / 3200  # Sekunden pro Frame

# ==========================================================
# SCHACHBRETT
# ==========================================================
SQUARE_SIZE = 0.05      # 5 cm
MIN_CORNERS = 4
MAX_CORNERS = 12

# ==========================================================
# TRACKER FACTORY
# ==========================================================
def create_csrt_tracker():
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()
    elif hasattr(cv2, "legacy"):
        return cv2.legacy.TrackerCSRT_create()
    else:
        raise RuntimeError("CSRT Tracker nicht verfügbar")

# ==========================================================
# VIDEO LADEN
# ==========================================================
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise IOError("Video konnte nicht geöffnet werden")

paused = False
tracking_active = False
roi = None
tracker = None

frame_index = 0
start_pos = None
meter_per_pixel = None
results = []

# ==========================================================
# PIXEL → METER AUS ERSTEM FRAME
# ==========================================================
ret, first_frame = cap.read()
if not ret:
    raise RuntimeError("Erstes Frame konnte nicht gelesen werden")

gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

best_corners = None
best_pattern = None
best_count = 0

for nx in range(MIN_CORNERS, MAX_CORNERS + 1):
    for ny in range(MIN_CORNERS, MAX_CORNERS + 1):
        found, corners = cv2.findChessboardCorners(gray, (nx, ny))
        if found and nx * ny > best_count:
            best_count = nx * ny
            best_pattern = (nx, ny)
            best_corners = corners

if best_corners is None:
    raise RuntimeError("Kein Schachbrett zur Skalierung gefunden")

best_corners = cv2.cornerSubPix(
    gray,
    best_corners,
    (11, 11),
    (-1, -1),
    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
)

# mittlerer Abstand benachbarter Ecken (horizontal)
distances = []
for i in range(best_pattern[0] - 1):
    p1 = best_corners[i]
    p2 = best_corners[i + 1]
    distances.append(np.linalg.norm(p2 - p1))

pixel_per_square = np.mean(distances)
meter_per_pixel = SQUARE_SIZE / pixel_per_square

print(f"Skalierung: {meter_per_pixel:.6e} m / Pixel")

# ==========================================================
# VIDEO ZURÜCKSETZEN
# ==========================================================
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

current_frame_gray = None

# ==========================================================
# HAUPTSCHLEIFE
# ==========================================================
while True:

    if not paused or tracking_active:
        ret, frame = cap.read()
        if not ret:
            break
        current_frame_gray = frame.copy()

    if len(current_frame_gray.shape) == 3:
        current_frame_gray = cv2.cvtColor(
            current_frame_gray, cv2.COLOR_BGR2GRAY
        )

    frame_bgr = cv2.cvtColor(current_frame_gray, cv2.COLOR_GRAY2BGR)

    # ------------------------------------------------------
    # TRACKING
    # ------------------------------------------------------
    if tracking_active:
        ok, bbox = tracker.update(frame_bgr)
        if ok:
            x, y, w, h = map(int, bbox)
            cx = x + w // 2
            cy = y + h // 2

            if start_pos is None:
                start_pos = (cx, cy)

            dx = cx - start_pos[0]
            dy = cy - start_pos[1]
            distance_m = np.sqrt(dx**2 + dy**2) * meter_per_pixel
            time_s = frame_index * DT

            results.append([frame_index, time_s, cx, cy, distance_m])

            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame_bgr, (cx, cy), 4, (0, 0, 255), -1)

            cv2.putText(
                frame_bgr,
                f"s = {distance_m:.3f} m",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2
            )

        else:
            cv2.putText(
                frame_bgr,
                "Tracking verloren",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

    # ------------------------------------------------------
    # INFO
    # ------------------------------------------------------
    cv2.putText(
        frame_bgr,
        "SPACE=stop | ROI ziehen | ENTER=start | ESC=Ende",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("Tracking", frame_bgr)

    key = cv2.waitKey(30) & 0xFF

    if key == 32 and not tracking_active:
        paused = True
        roi = cv2.selectROI("Tracking", frame_bgr, False, True)

    elif key == 13 and paused and roi is not None and not tracking_active:
        tracker = create_csrt_tracker()
        tracker.init(frame_bgr, roi)
        tracking_active = True
        paused = False

    elif key == 27:
        break

    frame_index += 1

# ==========================================================
# CSV SPEICHERN
# ==========================================================
with open(CSV_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["frame", "time_s", "x_px", "y_px", "distance_m"])
    writer.writerows(results)

# ==========================================================
# AUFRÄUMEN
# ==========================================================
cap.release()
cv2.destroyAllWindows()

print("Tracking beendet.")
print("CSV gespeichert unter:", CSV_PATH)

'''









import cv2
import numpy as np
import csv
import os

# ==========================================================
# DATA
# ==========================================================
VIDEO_PATH = "Videos/1_25_1_undistorted.mp4"

base_name = os.path.splitext(os.path.basename(VIDEO_PATH))[0]
csv_dir   = os.path.dirname(VIDEO_PATH)
CSV_PATH  = os.path.join(csv_dir, base_name + ".csv")

# ==========================================================
# ZEITBASIS
# ==========================================================
DT = 1 / 3200  # Sekunden pro Frame

# ==========================================================
# SCHACHBRETT
# ==========================================================
SQUARE_SIZE = 0.05
MIN_CORNERS = 4
MAX_CORNERS = 12

# ==========================================================
# TRACKER FACTORY
# ==========================================================
def create_csrt_tracker():
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()
    elif hasattr(cv2, "legacy"):
        return cv2.legacy.TrackerCSRT_create()
    else:
        raise RuntimeError("CSRT Tracker nicht verfügbar")

# ==========================================================
# VIDEO LADEN
# ==========================================================
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise IOError("Video konnte nicht geöffnet werden")

paused = False
tracking_active = False
roi = None
tracker = None
roi_frame = None

start_pos = None
meter_per_pixel = None
results = []

tracking_frame_index = 0

# ==========================================================
# PIXEL → METER AUS ERSTEM FRAME
# ==========================================================
ret, first_frame = cap.read()
if not ret:
    raise RuntimeError("Erstes Frame konnte nicht gelesen werden")

gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

best_corners = None
best_pattern = None
best_count = 0

for nx in range(MIN_CORNERS, MAX_CORNERS + 1):
    for ny in range(MIN_CORNERS, MAX_CORNERS + 1):
        found, corners = cv2.findChessboardCorners(gray, (nx, ny))
        if found and nx * ny > best_count:
            best_count = nx * ny
            best_pattern = (nx, ny)
            best_corners = corners

if best_corners is None:
    raise RuntimeError("Kein Schachbrett zur Skalierung gefunden")

best_corners = cv2.cornerSubPix(
    gray, best_corners, (11, 11), (-1, -1),
    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
)

distances = []
for i in range(best_pattern[0] - 1):
    distances.append(np.linalg.norm(best_corners[i + 1] - best_corners[i]))

pixel_per_square = np.mean(distances)
meter_per_pixel = SQUARE_SIZE / pixel_per_square

print(f"Skalierung: {meter_per_pixel:.6e} m / Pixel")

# ==========================================================
# VIDEO ZURÜCKSETZEN
# ==========================================================
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# ==========================================================
# HAUPTSCHLEIFE
# ==========================================================
while True:

    if not paused or tracking_active:
        ret, frame = cap.read()
        if not ret:
            break

    frame_bgr = frame.copy()

    # ------------------------------------------------------
    # TRACKING
    # ------------------------------------------------------
    if tracking_active:
        ok, bbox = tracker.update(frame_bgr)
        if ok:
            x, y, w, h = map(int, bbox)
            cx = x + w // 2
            cy = y + h // 2

            if start_pos is None:
                start_pos = (cx, cy)

            dx = cx - start_pos[0]
            dy = cy - start_pos[1]
            distance_m = np.sqrt(dx*dx + dy*dy) * meter_per_pixel

            frame_csv = tracking_frame_index + 1
            time_s = tracking_frame_index * DT

            results.append([frame_csv, time_s, cx, cy, distance_m])
            tracking_frame_index += 1

            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame_bgr, (cx, cy), 4, (0, 0, 255), -1)

        else:
            cv2.putText(
                frame_bgr,
                "Tracking verloren",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

    # ------------------------------------------------------
    # INFO
    # ------------------------------------------------------
    cv2.putText(
        frame_bgr,
        "SPACE=ROI | ENTER=Start | ESC=Ende",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("Tracking", frame_bgr)
    key = cv2.waitKey(30) & 0xFF

    # ------------------------------------------------------
    # ROI AUSWAHL
    # ------------------------------------------------------
    if key == 32 and not tracking_active:
        paused = True
        roi_frame = frame_bgr.copy()  # <<< exakt dieses Frame merken
        roi = cv2.selectROI("Tracking", roi_frame, False, True)

    # ------------------------------------------------------
    # TRACKER STARTEN (EXAKT GLEICHES FRAME)
    # ------------------------------------------------------
    elif key == 13 and paused and roi is not None and not tracking_active:
        tracker = create_csrt_tracker()
        tracker.init(roi_frame, roi)
        tracking_active = True
        paused = False
        start_pos = None
        tracking_frame_index = 0

    elif key == 27:
        break

# ==========================================================
# CSV SPEICHERN
# ==========================================================
with open(CSV_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["frame", "time_s", "x_px", "y_px", "distance_m"])
    writer.writerows(results)

# ==========================================================
# AUFRÄUMEN
# ==========================================================
cap.release()
cv2.destroyAllWindows()

print("Tracking beendet.")
print("CSV gespeichert unter:", CSV_PATH)
