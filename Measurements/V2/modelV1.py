import cv2
import numpy as np
import os
from skimage.feature import hog
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# ==========================================================
# PFADE
# ==========================================================
PUCK_DIR = "puckData/150x150"
BG_DIR = "backgroundData/150x150"
MODEL_FILE = "puck_detector_svm.joblib"

# ==========================================================
# PARAMETER
# ==========================================================
PATCH_SIZE = (150, 150)   # Pixel
TRAIN_RATIO = 0.80        # 20 % Training, 80 % Test (wie gefordert)

HOG_PARAMS = {
    "orientations": 9,
    "pixels_per_cell": (8, 8),
    "cells_per_block": (2, 2),
    "block_norm": "L2-Hys"
}

# ==========================================================
# HOG FEATURE-EXTRAKTION
# ==========================================================
def extract_hog(img):
    return hog(
        img,
        orientations=HOG_PARAMS["orientations"],
        pixels_per_cell=HOG_PARAMS["pixels_per_cell"],
        cells_per_block=HOG_PARAMS["cells_per_block"],
        block_norm=HOG_PARAMS["block_norm"]
    )

# ==========================================================
# DATEN LADEN
# ==========================================================
X = []
y = []

def load_images(folder, label):
    for fname in os.listdir(folder):
        path = os.path.join(folder, fname)

        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        # Sicherheit: auf 150x150 bringen
        if img.shape != PATCH_SIZE:
            img = cv2.resize(img, PATCH_SIZE, interpolation=cv2.INTER_AREA)

        features = extract_hog(img)
        X.append(features)
        y.append(label)

print("Lade Puck-Daten...")
load_images(PUCK_DIR, label=1)

print("Lade Hintergrund-Daten...")
load_images(BG_DIR, label=0)

X = np.array(X)
y = np.array(y)

print("\n================= DATEN =================")
print(f"Gesamt Samples: {len(X)}")
print(f"Puck: {np.sum(y == 1)}")
print(f"Background: {np.sum(y == 0)}")

# ==========================================================
# TRAIN / TEST SPLIT
# ==========================================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    train_size=TRAIN_RATIO,
    random_state=42,
    stratify=y
)

print("\n================= SPLIT =================")
print(f"Training: {len(X_train)} Samples ({TRAIN_RATIO*100:.0f} %)")
print(f"Test:     {len(X_test)} Samples ({(1-TRAIN_RATIO)*100:.0f} %)")

# ==========================================================
# MODELL TRAINIEREN
# ==========================================================
clf = LinearSVC(
    C=1.0,
    max_iter=10000
)

print("\nTrainiere SVM-Modell...")
clf.fit(X_train, y_train)

# ==========================================================
# EVALUATION
# ==========================================================
y_pred = clf.predict(X_test)

print("\n================= ERGEBNIS =================")
print(classification_report(
    y_test,
    y_pred,
    target_names=["Background", "Puck"]
))

# ==========================================================
# MODELL SPEICHERN
# ==========================================================
joblib.dump(
    {
        "model": clf,
        "patch_size": PATCH_SIZE,
        "hog_params": HOG_PARAMS
    },
    MODEL_FILE
)

print(f"\nModell gespeichert als: {MODEL_FILE}")
