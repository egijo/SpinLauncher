import cv2
import numpy as np
import joblib
from skimage.feature import hog

# ==========================================================
# DATEIEN
# ==========================================================
IMAGE_PATH = "test_image.png"          # großes Testbild
MODEL_FILE = "puck_detector_svm.joblib"
OUTPUT_IMAGE = "result.png"

# ==========================================================
# MODELL LADEN
# ==========================================================
data = joblib.load(MODEL_FILE)
clf = data["model"]
PATCH_SIZE = data["patch_size"]
hog_params = data["hog_params"]

# ==========================================================
# HOG FEATURE
# ==========================================================
def extract_hog(img):
    return hog(
        img,
        orientations=hog_params["orientations"],
        pixels_per_cell=hog_params["pixels_per_cell"],
        cells_per_block=hog_params["cells_per_block"],
        block_norm="L2-Hys"
    )

# ==========================================================
# BILD LADEN
# ==========================================================
img = cv2.imread(IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
if img is None:
    raise IOError("Bild konnte nicht geladen werden")

H, W = img.shape
vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

# ==========================================================
# SLIDING WINDOW PARAMETER
# ==========================================================
STEP = PATCH_SIZE[0] // 4   # z.B. 1/4 Patchüberlappung
THRESHOLD = 0.0             # Entscheidungsgrenze

best_score = -1e9
best_center = None
best_box = None

# ==========================================================
# SLIDING WINDOW
# ==========================================================
for y in range(0, H - PATCH_SIZE[1] + 1, STEP):
    for x in range(0, W - PATCH_SIZE[0] + 1, STEP):
        patch = img[y:y+PATCH_SIZE[1], x:x+PATCH_SIZE[0]]

        features = extract_hog(patch)
        score = clf.decision_function([features])[0]

        if score > best_score:
            best_score = score
            best_center = (
                x + PATCH_SIZE[0] // 2,
                y + PATCH_SIZE[1] // 2
            )
            best_box = (x, y, x + PATCH_SIZE[0], y + PATCH_SIZE[1])

# ==========================================================
# AUSWERTUNG
# ==========================================================
print(f"Best score im Bild: {best_score:.3f}")

if best_score > THRESHOLD:
    print("✅ Puck gefunden")

    x1, y1, x2, y2 = best_box
    cx, cy = best_center

    cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.circle(vis, (cx, cy), 5, (0, 0, 255), -1)

else:
    print("❌ Kein Puck im Bild erkannt")

# ==========================================================
# SPEICHERN & ANZEIGEN
# ==========================================================
cv2.imwrite(OUTPUT_IMAGE, vis)
cv2.imshow("Result", vis)
cv2.waitKey(0)
cv2.destroyAllWindows()
