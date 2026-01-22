'''import cv2
import numpy as np
import os

# ==========================================================
# DATEIEN
# ==========================================================
VIDEO_IN  = "Videos/27_55_2.mp4"
#VIDEO_OUT = VIDEO_IN + "_undistorted.mp4"

base_name = os.path.splitext(os.path.basename(VIDEO_IN))[0]
csv_dir   = os.path.dirname(VIDEO_IN)
VIDEO_OUT  = os.path.join(csv_dir, base_name + "_undistorted.mp4")

# ==========================================================
# SCHACHBRETT
# ==========================================================
SQUARE_SIZE = 0.05   # 5 cm
MIN_CORNERS = 4
MAX_CORNERS = 12

# ==========================================================
# VIDEO & ERSTES FRAME
# ==========================================================
cap = cv2.VideoCapture(VIDEO_IN)
if not cap.isOpened():
    raise IOError("Video konnte nicht geöffnet werden")

fps    = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

ret, frame0 = cap.read()
if not ret:
    raise RuntimeError("Erstes Frame konnte nicht gelesen werden")

gray = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)

# ==========================================================
# AUTOMATISCHE MUSTERSUCHE
# ==========================================================
best_pattern = None
best_corners = None
best_count = 0

for nx in range(MIN_CORNERS, MAX_CORNERS + 1):
    for ny in range(MIN_CORNERS, MAX_CORNERS + 1):
        pattern = (nx, ny)
        found, corners = cv2.findChessboardCorners(gray, pattern)

        if found:
            count = nx * ny
            if count > best_count:
                best_count = count
                best_pattern = pattern
                best_corners = corners

if best_corners is None:
    raise RuntimeError("Kein Schachbrettmuster erkannt")


# ==========================================================
# SUBPIXEL-VERFEINERUNG
# ==========================================================
best_corners = cv2.cornerSubPix(
    gray,
    best_corners,
    (11, 11),
    (-1, -1),
    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
)

# ==========================================================
# ANZEIGE + USER BESTÄTIGUNG
# ==========================================================
vis = frame0.copy()
cv2.drawChessboardCorners(vis, best_pattern, best_corners, True)

cv2.putText(
    vis,
    f"Erkannt: {best_pattern[0]} x {best_pattern[1]} Innenecken",
    (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.0,
    (0, 255, 0),
    2
)

cv2.putText(
    vis,
    "ENTER = bestaetigen | ESC = abbrechen",
    (20, 80),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0, 255, 0),
    2
)

cv2.imshow("Erkannte Schachbrettecken", vis)

while True:
    key = cv2.waitKey(0) & 0xFF
    if key == 13:   # ENTER
        break
    elif key == 27: # ESC
        cap.release()
        cv2.destroyAllWindows()
        raise RuntimeError("Abgebrochen durch User")

cv2.destroyAllWindows()

print("✔ Muster bestaetigt:", best_pattern)

# ==========================================================
# OBJEKTPUNKTE
# ==========================================================
objp = np.zeros((best_pattern[0] * best_pattern[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:best_pattern[0], 0:best_pattern[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

# ==========================================================
# KAMERAKALIBRIERUNG
# ==========================================================
ret, K, dist, _, _ = cv2.calibrateCamera(
    [objp],
    [best_corners],
    gray.shape[::-1],
    None,
    None
)

np.save("camera_matrix.npy", K)
np.save("dist_coeffs.npy", dist)

#print("✔ Kamerakalibrierung abgeschlossen")

# ==========================================================
# VIDEO-WRITER
# ==========================================================
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(VIDEO_OUT, fourcc, fps, (width, height))

# ==========================================================
# ERSTES FRAME
# ==========================================================
out.write(cv2.undistort(frame0, K, dist))

# ==========================================================
# RESTLICHES VIDEO
# ==========================================================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_undistorted = cv2.undistort(frame, K, dist)
    out.write(frame_undistorted)

# ==========================================================
# AUFRÄUMEN
# ==========================================================
cap.release()
out.release()

print("🎉 Entzerrtes Video gespeichert als:", VIDEO_OUT)

'''

'''

import cv2
import numpy as np
import os

# ==========================================================
# DATEIEN
# ==========================================================
VIDEO_IN = "Videos/27_55_2.mp4"

base_name = os.path.splitext(os.path.basename(VIDEO_IN))[0]
video_dir = os.path.dirname(VIDEO_IN)
VIDEO_OUT = os.path.join(video_dir, base_name + "_undistorted.mp4")

CAMERA_MATRIX_PATH = "camera_matrix.npy"
DIST_COEFFS_PATH   = "dist_coeffs.npy"

# ==========================================================
# KAMERAPARAMETER LADEN
# ==========================================================
if not os.path.exists(CAMERA_MATRIX_PATH):
    raise FileNotFoundError("camera_matrix.npy nicht gefunden")

if not os.path.exists(DIST_COEFFS_PATH):
    raise FileNotFoundError("dist_coeffs.npy nicht gefunden")

K    = np.load(CAMERA_MATRIX_PATH)
dist = np.load(DIST_COEFFS_PATH)

print("✔ Kameraparameter geladen")

# ==========================================================
# VIDEO ÖFFNEN
# ==========================================================
cap = cv2.VideoCapture(VIDEO_IN)
if not cap.isOpened():
    raise IOError("Video konnte nicht geöffnet werden")

fps    = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# ==========================================================
# VIDEO-WRITER
# ==========================================================
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(VIDEO_OUT, fourcc, fps, (width, height))

# ==========================================================
# VIDEO ENZERRUNG
# ==========================================================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_undistorted = cv2.undistort(frame, K, dist)
    out.write(frame_undistorted)

# ==========================================================
# AUFRÄUMEN
# ==========================================================
cap.release()
out.release()

print("🎉 Entzerrtes Video gespeichert als:")
print(VIDEO_OUT)


'''

import cv2
import numpy as np
import os

# ==========================================================
# DATEIEN
# ==========================================================
VIDEO_IN  = "Videos/27_55_2.mp4"

base_name = os.path.splitext(os.path.basename(VIDEO_IN))[0]
csv_dir   = os.path.dirname(VIDEO_IN)
VIDEO_OUT = os.path.join(csv_dir, base_name + "_undistorted.mp4")

CHESSBOARD_DATA_PATH = os.path.join(csv_dir, base_name + "_chessboard.npz")

# ==========================================================
# SCHACHBRETT
# ==========================================================
SQUARE_SIZE = 0.05   # 5 cm
MIN_CORNERS = 4
MAX_CORNERS = 12

# ==========================================================
# VIDEO & ERSTES FRAME
# ==========================================================
cap = cv2.VideoCapture(VIDEO_IN)
if not cap.isOpened():
    raise IOError("Video konnte nicht geöffnet werden")

fps    = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

ret, frame0 = cap.read()
if not ret:
    raise RuntimeError("Erstes Frame konnte nicht gelesen werden")

gray = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)

# ==========================================================
# AUTOMATISCHE MUSTERSUCHE
# ==========================================================
best_pattern = None
best_corners = None
best_count = 0

for nx in range(MIN_CORNERS, MAX_CORNERS + 1):
    for ny in range(MIN_CORNERS, MAX_CORNERS + 1):
        pattern = (nx, ny)
        found, corners = cv2.findChessboardCorners(gray, pattern)

        if found:
            count = nx * ny
            if count > best_count:
                best_count = count
                best_pattern = pattern
                best_corners = corners

if best_corners is None:
    raise RuntimeError("Kein Schachbrettmuster erkannt")

# ==========================================================
# SUBPIXEL-VERFEINERUNG
# ==========================================================
best_corners = cv2.cornerSubPix(
    gray,
    best_corners,
    (11, 11),
    (-1, -1),
    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
)

# ==========================================================
# SPEICHERN: PATTERN + CORNERS
# ==========================================================
np.savez(
    CHESSBOARD_DATA_PATH,
    pattern=np.array(best_pattern, dtype=np.int32),
    corners=best_corners.astype(np.float32)
)

print("✔ Schachbrettdaten gespeichert unter:")
print(CHESSBOARD_DATA_PATH)

# ==========================================================
# ANZEIGE + USER BESTÄTIGUNG
# ==========================================================
vis = frame0.copy()
cv2.drawChessboardCorners(vis, best_pattern, best_corners, True)

cv2.putText(
    vis,
    f"Erkannt: {best_pattern[0]} x {best_pattern[1]} Innenecken",
    (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.0,
    (0, 255, 0),
    2
)

cv2.putText(
    vis,
    "ENTER = bestaetigen | ESC = abbrechen",
    (20, 80),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0, 255, 0),
    2
)

cv2.imshow("Erkannte Schachbrettecken", vis)

while True:
    key = cv2.waitKey(0) & 0xFF
    if key == 13:
        break
    elif key == 27:
        cap.release()
        cv2.destroyAllWindows()
        raise RuntimeError("Abgebrochen durch User")

cv2.destroyAllWindows()

print("✔ Muster bestaetigt:", best_pattern)

# ==========================================================
# OBJEKTPUNKTE
# ==========================================================
objp = np.zeros((best_pattern[0] * best_pattern[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:best_pattern[0], 0:best_pattern[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

# ==========================================================
# KAMERAKALIBRIERUNG
# ==========================================================
ret, K, dist, _, _ = cv2.calibrateCamera(
    [objp],
    [best_corners],
    gray.shape[::-1],
    None,
    None
)

#np.save("camera_matrix.npy", K)
#np.save("dist_coeffs.npy", dist)

# ==========================================================
# VIDEO-WRITER
# ==========================================================
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(VIDEO_OUT, fourcc, fps, (width, height))

out.write(cv2.undistort(frame0, K, dist))

while True:
    ret, frame = cap.read()
    if not ret:
        break
    out.write(cv2.undistort(frame, K, dist))

cap.release()
out.release()

print("🎉 Entzerrtes Video gespeichert als:", VIDEO_OUT)
