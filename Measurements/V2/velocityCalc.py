import cv2
import numpy as np
import re
import math

# ==========================================================
# DATEIEN
# ==========================================================
IMG1 = "frame_1_videoFrame_75_marked.png"
IMG2 = "frame_2_videoFrame_149_marked.png"
CALIB_FILE = "camera_calibration.npz"

FPS = 3200.0

# ==========================================================
# GEOMETRIE
# ==========================================================
SQUARE_SIZE = 50.0            # mm (5 cm)
PUCK_ABOVE_BOARD = 70.0       # mm
PUCK_HEIGHT = 25.4            # mm
PUCK_Z = PUCK_ABOVE_BOARD + PUCK_HEIGHT / 2.0

# ==========================================================
# FRAME-NUMMER AUS DATEINAMEN
# ==========================================================
def extract_frame_number(fname):
    m = re.search(r"videoFrame_(\d+)", fname)
    if not m:
        raise ValueError(f"Keine Frame-Nummer in {fname}")
    return int(m.group(1))

frame1 = extract_frame_number(IMG1)
frame2 = extract_frame_number(IMG2)
dt = abs(frame2 - frame1) / FPS   # Sekunden

print(f"Δt = {dt:.6f} s")

# ==========================================================
# KALIBRIERUNG LADEN
# ==========================================================
calib = np.load(CALIB_FILE)
cameraMatrix = calib["cameraMatrix"]
distCoeffs = calib["distCoeffs"]
rvec = calib["rvec"]
tvec = calib["tvec"]

R, _ = cv2.Rodrigues(rvec)

# ==========================================================
# MITTELPUNKT AUS MARKIERTEM BILD FINDEN
# ==========================================================
def find_red_center(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise IOError(f"Bild {img_path} nicht gefunden")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Rotbereich (2 Zonen)
    mask1 = cv2.inRange(hsv, (0, 120, 70), (10, 255, 255))
    mask2 = cv2.inRange(hsv, (170, 120, 70), (180, 255, 255))
    mask = mask1 | mask2

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise RuntimeError(f"Kein Mittelpunkt in {img_path} gefunden")

    cnt = max(contours, key=cv2.contourArea)
    M = cv2.moments(cnt)

    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]

    return np.array([cx, cy], dtype=np.float32)

p1_px = find_red_center(IMG1)
p2_px = find_red_center(IMG2)

print("Pixelkoordinaten:")
print("P1:", p1_px)
print("P2:", p2_px)

# ==========================================================
# PIXEL → STRAHL → SCHNITT MIT Z = PUCK_Z
# ==========================================================
def pixel_to_world(pixel):
    # undistort & normalisieren
    pts = np.array([[pixel]], dtype=np.float32)
    undist = cv2.undistortPoints(pts, cameraMatrix, distCoeffs)
    x, y = undist[0, 0]

    # Strahl im Kamerakoordinatensystem
    ray_cam = np.array([x, y, 1.0])
    ray_world = R.T @ ray_cam

    cam_center = -R.T @ tvec.flatten()

    # Schnitt mit Ebene Z = PUCK_Z
    scale = (PUCK_Z - cam_center[2]) / ray_world[2]
    world_point = cam_center + scale * ray_world

    return world_point

P1 = pixel_to_world(p1_px)
P2 = pixel_to_world(p2_px)

# ==========================================================
# DISTANZ & GESCHWINDIGKEIT
# ==========================================================
distance_mm = np.linalg.norm(P2 - P1)
distance_m = distance_mm / 1000.0

speed_m_s = distance_m / dt
speed_kmh = speed_m_s * 3.6

# ==========================================================
# ERGEBNIS
# ==========================================================
print("\n================ ERGEBNIS ================")
print(f"Strecke: {distance_mm:.2f} mm")
print(f"Zeit:    {dt*1000:.3f} ms")
print(f"Speed:   {speed_kmh:.2f} km/h")
