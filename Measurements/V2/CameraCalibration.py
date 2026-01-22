import cv2
import numpy as np
import glob
import os
import sys

# ==========================================================
# EINSTELLUNGEN
# ==========================================================

IMAGE_DIR = "calibration_images"   # Ordner mit Kalibrierbildern
IMAGE_EXTENSIONS = ("*.png", "*.jpg", "*.jpeg", "*.tif", "*.tiff")

CHECKERBOARD = (4, 5)      # (Spalten, Zeilen) innere Ecken
SQUARE_SIZE = 35.0         # mm (!!! exakt messen !!!)

OUTPUT_FILE_NPZ = "camera_calibration.npz"
OUTPUT_FILE_YAML = "camera_calibration.yaml"

# ==========================================================
# OBJEKTPUNKTE (WELTKOORDINATEN)
# ==========================================================

objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

objpoints = []  # 3D Punkte
imgpoints = []  # 2D Punkte

# ==========================================================
# BILDER LADEN
# ==========================================================

image_files = []
for ext in IMAGE_EXTENSIONS:
    image_files.extend(glob.glob(os.path.join(IMAGE_DIR, ext)))

if len(image_files) < 5:
    print("FEHLER: Zu wenige Bilder gefunden!")
    sys.exit(1)

print(f"{len(image_files)} Bilder gefunden")

image_size = None

# ==========================================================
# SCHACHBRETT-ECKEN ERKENNEN
# ==========================================================

for fname in image_files:
    img = cv2.imread(fname, cv2.IMREAD_UNCHANGED)

    if img is None:
        print(f"Warnung: {fname} konnte nicht geladen werden")
        continue

    if img.dtype == np.uint16:
        img = (img / 256).astype(np.uint8)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img

    if image_size is None:
        image_size = gray.shape[::-1]

    ret, corners = cv2.findChessboardCorners(
        gray,
        CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH +
        cv2.CALIB_CB_NORMALIZE_IMAGE
    )

    if not ret:
        print(f"Schachbrett NICHT gefunden: {fname}")
        continue

    corners = cv2.cornerSubPix(
        gray,
        corners,
        (11, 11),
        (-1, -1),
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    )

    objpoints.append(objp)
    imgpoints.append(corners)

    print(f"OK: {fname}")

if len(objpoints) < 5:
    print("FEHLER: Zu wenige gültige Kalibrierbilder!")
    sys.exit(1)

# ==========================================================
# KAMERAKALIBRIERUNG
# ==========================================================

ret, cameraMatrix, distCoeffs, rvecs, tvecs = cv2.calibrateCamera(
    objpoints,
    imgpoints,
    image_size,
    None,
    None
)

print("\n================= KALIBRIERUNG =================")
print(f"RMS Reprojection Error: {ret:.4f}")
print("Kameramatrix:\n", cameraMatrix)
print("Distortion:\n", distCoeffs.ravel())

# ==========================================================
# KAMERAHÖHE (solvePnP mit erstem Bild)
# ==========================================================

success, rvec, tvec = cv2.solvePnP(
    objpoints[0],
    imgpoints[0],
    cameraMatrix,
    distCoeffs,
    flags=cv2.SOLVEPNP_ITERATIVE
)

if not success:
    print("FEHLER: solvePnP fehlgeschlagen!")
    sys.exit(1)

camera_height_mm = abs(float(tvec[2]))
camera_height_cm = camera_height_mm / 10.0

print("\n================= DISTANZ =================")
print(f"Kamerahöhe (optisches Zentrum → Boden): {camera_height_cm:.2f} cm")

# ==========================================================
# SPEICHERN
# ==========================================================

np.savez(
    OUTPUT_FILE_NPZ,
    cameraMatrix=cameraMatrix,
    distCoeffs=distCoeffs,
    rvec=rvec,
    tvec=tvec,
    rms=ret
)

fs = cv2.FileStorage(OUTPUT_FILE_YAML, cv2.FILE_STORAGE_WRITE)
fs.write("cameraMatrix", cameraMatrix)
fs.write("distCoeffs", distCoeffs)
fs.write("rvec", rvec)
fs.write("tvec", tvec)
fs.write("rms", ret)
fs.release()

print("\nKalibrierung gespeichert:")
print(f" - {OUTPUT_FILE_NPZ}")
print(f" - {OUTPUT_FILE_YAML}")
