'''import cv2
import numpy as np

# ==========================================================
# DATEI
# ==========================================================
VIDEO_PATH = "Videos/27_55_2.mp4"

# ==========================================================
# STATUS
# ==========================================================
paused = False
drawing = False
ix, iy = -1, -1
rect = None
saved_frames = 0
current_frame = None

# ==========================================================
# MAUS CALLBACK (nur grobe ROI)
# ==========================================================
def mouse_callback(event, x, y, flags, param):
    global ix, iy, drawing, rect

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        rect = None

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        rect = (ix, iy, x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect = (ix, iy, x, y)

# ==========================================================
# AUTOMATISCHE PUCK-ERKENNUNG IN ROI
# ==========================================================
def detect_puck_in_roi(frame, rect):
    x1, y1, x2, y2 = rect
    x1, x2 = sorted([x1, x2])
    y1, y2 = sorted([y1, y2])

    roi = frame[y1:y2, x1:x2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # --- Vorverarbeitung ---
    blur = cv2.GaussianBlur(gray, (9, 9), 0)

    # automatische Schwelle
    _, thresh = cv2.threshold(
        blur, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # kleine Störungen entfernen
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    # --- Konturen ---
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return frame, None

    # größte Kontur = Puck
    cnt = max(contours, key=cv2.contourArea)

    # Kreisfit
    (cx, cy), radius = cv2.minEnclosingCircle(cnt)
    cx, cy, radius = int(cx), int(cy), int(radius)

    # Koordinaten ins Gesamtbild transformieren
    cx_global = x1 + cx
    cy_global = y1 + cy

    # Zeichnen
    cv2.circle(frame, (cx_global, cy_global), radius, (0, 255, 0), 2)
    cv2.circle(frame, (cx_global, cy_global), 4, (0, 0, 255), -1)

    return frame, (cx_global, cy_global)

# ==========================================================
# VIDEO
# ==========================================================
cap = cv2.VideoCapture(VIDEO_PATH)
cv2.namedWindow("Video")
cv2.setMouseCallback("Video", mouse_callback)

while cap.isOpened():
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break
        current_frame = frame.copy()

    display = current_frame.copy()

    # ROI anzeigen
    if rect:
        x1, y1, x2, y2 = rect
        cv2.rectangle(display, (x1, y1), (x2, y2), (255, 0, 0), 2)

    cv2.imshow("Video", display)
    key = cv2.waitKey(30) & 0xFF

    # SPACE → Pause / Weiter
    if key == 32:
        paused = not paused

    # ENTER → ROI auswerten
    elif key == 13 and paused and rect is not None:
        result, center = detect_puck_in_roi(
            current_frame.copy(), rect
        )

        saved_frames += 1
        filename = f"frame_{saved_frames}_marked.png"
        cv2.imwrite(filename, result)

        print(f"Frame {saved_frames} gespeichert")
        if center:
            print(f"  Mittelpunkt: {center}")
        else:
            print("  ❌ Kein Puck im ROI gefunden")

        rect = None
        paused = False

        if saved_frames >= 2:
            break

    # ESC → Abbruch
    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()
print("Fertig.")

'''


import cv2
import numpy as np

# ==========================================================
# DATEI
# ==========================================================
VIDEO_PATH = "Videos/27_55_2.mp4"

# ==========================================================
# STATUS
# ==========================================================
paused = False
current_frame = None

center = None
radius = 30

saved_frames = 0
frame_index = 0   # <<< Frame-Zähler

# ==========================================================
# MAUS CALLBACK
# ==========================================================
def mouse_callback(event, x, y, flags, param):
    global center, radius

    # Mittelpunkt setzen
    if event == cv2.EVENT_LBUTTONDOWN:
        center = (x, y)

    # Radius mit Mausrad ändern
    elif event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            radius += 2
        else:
            radius = max(5, radius - 2)

cv2.namedWindow("Video")
cv2.setMouseCallback("Video", mouse_callback)

# ==========================================================
# VIDEO
# ==========================================================
cap = cv2.VideoCapture(VIDEO_PATH)

while cap.isOpened():
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break

        current_frame = frame.copy()
        frame_index += 1   # <<< Frame mitzählen

    display = current_frame.copy()

    # Kreis zeichnen
    if center is not None:
        cv2.circle(display, center, radius, (0, 255, 0), 2)
        cv2.circle(display, center, 4, (0, 0, 255), -1)

    cv2.putText(
        display,
        f"Video-Frame: {frame_index} | SPACE=pause | Klick=Mittelpunkt | Mausrad=Radius | ENTER=speichern",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("Video", display)
    key = cv2.waitKey(30) & 0xFF

    # SPACE → Pause / Weiter
    if key == 32:
        paused = not paused

    # ENTER → Speichern
    elif key == 13 and paused and center is not None:
        out = current_frame.copy()
        cv2.circle(out, center, radius, (0, 255, 0), 2)
        cv2.circle(out, center, 4, (0, 0, 255), -1)

        saved_frames += 1
        filename = f"frame_{saved_frames}_videoFrame_{frame_index}_marked.png"
        cv2.imwrite(filename, out)

        print(f"Gespeichert: {filename}")
        print(f"  Mittelpunkt: {center}, Radius: {radius}")

        # Reset für nächsten Marker
        center = None
        radius = 30
        paused = False

        if saved_frames >= 2:
            break

    # ESC → Abbruch
    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()
print("Fertig.")
