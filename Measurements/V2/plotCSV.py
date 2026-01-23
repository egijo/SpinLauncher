'''import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# DATEI
# ==========================================================
CSV_PATH = "Videos/8_25_8_undistorted.csv"

# ==========================================================
# CSV LADEN
# ==========================================================
df = pd.read_csv(CSV_PATH)
t = 0.04

# Sicherheit: nach Zeit sortieren
df = df.sort_values("time_s").reset_index(drop=True)

# ==========================================================
# DISTANZ–ZEIT–PLOT
# ==========================================================
plt.figure()
plt.plot(df["time_s"], df["distance_m"])
plt.xlabel("Zeit [s]")
plt.ylabel("Distanz [m]")
plt.title("Zurückgelegte Distanz über der Zeit")
plt.grid(True)
plt.tight_layout()
plt.show()

# ==========================================================
# GESCHWINDIGKEIT ZWISCHEN 0 s UND 1 s
# ==========================================================
df_0_1 = df[(df["time_s"] >= 0.0) & (df["time_s"] <= t)]

if len(df_0_1) < 2:
    raise RuntimeError("Nicht genügend Datenpunkte zwischen 0 s und 1 s")

t0 = df_0_1["time_s"].iloc[0]
t1 = df_0_1["time_s"].iloc[-1]

s0 = df_0_1["distance_m"].iloc[0]
s1 = df_0_1["distance_m"].iloc[-1]

v_ms = (s1 - s0) / (t1 - t0)      # m/s
v_kmh = v_ms * 3.6               # km/h

# ==========================================================
# AUSGABE
# ==========================================================
print("===================================")
print("Geschwindigkeit zwischen 0 s und 1 s")
print(f"Δs = {s1 - s0:.4f} m")
print(f"Δt = {t1 - t0:.4f} s")
print(f"v  = {v_ms:.3f} m/s")
print(f"v  = {v_kmh:.2f} km/h")
print("===================================")
'''



'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ==========================================================
# EINSTELLUNG: MAXIMALE ZEIT
# ==========================================================
T_MAX = 0.05   # Sekunden (HIER ANPASSEN)


# ==========================================================
# CSV-DATEIEN (HIER DEFINIEREN)
# ==========================================================
CSV_FILES = [
    "Videos/1_25_1_undistorted.csv",
    "Videos/2_25_2_undistorted.csv",
    "Videos/3_25_3_undistorted.csv",
    "Videos/4_25_4_undistorted.csv",
    "Videos/5_25_5_undistorted.csv",
    "Videos/6_25_6_undistorted.csv",
    "Videos/7_25_7_undistorted.csv",
    "Videos/8_25_8_undistorted.csv",
    "Videos/9_25_9_undistorted.csv",
    "Videos/10_25_10_undistorted.csv",
    "Videos/11_25_11_undistorted.csv",
]

# ==========================================================
# VERARBEITUNG JE CSV
# ==========================================================
print("\n===================================")
print(f"Auswertung bis t = {T_MAX} s")
print("===================================")

for path in CSV_FILES:

    # ------------------------------------------------------
    # CSV LADEN
    # ------------------------------------------------------
    df = pd.read_csv(path)

    if not {"time_s", "distance_m"}.issubset(df.columns):
        raise ValueError(f"CSV {path} hat nicht das erwartete Format")

    df = df.sort_values("time_s").reset_index(drop=True)

    # ------------------------------------------------------
    # AUF ZEITFENSTER BESCHRÄNKEN
    # ------------------------------------------------------
    df = df[df["time_s"] <= T_MAX]

    if len(df) < 2:
        print(f"{path}: zu wenige Datenpunkte bis {T_MAX}s")
        continue

    # ------------------------------------------------------
    # GESCHWINDIGKEIT (0 → T_MAX)
    # ------------------------------------------------------
    t0 = df["time_s"].iloc[0]
    t1 = df["time_s"].iloc[-1]

    s0 = df["distance_m"].iloc[0]
    s1 = df["distance_m"].iloc[-1]

    v_ms = (s1 - s0) / (t1 - t0)
    v_kmh = v_ms * 3.6

    print(f"{path}")
    print(f"  Δs = {s1 - s0:.4f} m")
    print(f"  Δt = {t1 - t0:.6f} s")
    print(f"  v  = {v_ms:.3f} m/s = {v_kmh:.2f} km/h")
    print("-----------------------------------")

    # ------------------------------------------------------
    # PLOT
    # ------------------------------------------------------
    plt.figure(figsize=(7, 4))
    plt.plot(
        df["time_s"],
        df["distance_m"],
        linewidth=1.5
    )

    plt.xlabel("Zeit [s]")
    plt.ylabel("Distanz [m]")
    plt.title(f"Distanz über Zeit (bis {T_MAX}s)\n{path}")
    plt.xlim(0, T_MAX)
    plt.ylim(bottom=0)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# EINSTELLUNG: MAXIMALE ZEIT
# ==========================================================
T_MAX = 0.05   # Sekunden

# ==========================================================
# CSV-DATEIEN
# ==========================================================
CSV_FILES = [
    "Videos/1_25_1_undistorted.csv",
    "Videos/2_25_2_undistorted.csv",
    "Videos/3_25_3_undistorted.csv",
    "Videos/4_25_4_undistorted.csv",
    "Videos/5_25_5_undistorted.csv",
    "Videos/6_25_6_undistorted.csv",
    "Videos/7_25_7_undistorted.csv",
    "Videos/8_25_8_undistorted.csv",
    "Videos/9_25_9_undistorted.csv",
    #"Videos/10_25_10_undistorted.csv",
    "Videos/11_25_11_undistorted.csv",
    #"Videos/12_25_12_undistorted.csv",
    "Videos/13_25_13_undistorted.csv",
    #"Videos/14_25_14_undistorted.csv",
]

# ==========================================================
# CSVs LADEN UND BESCHNEIDEN
# ==========================================================
dataframes = []
velocities_ms = []

for path in CSV_FILES:
    df = pd.read_csv(path)

    if not {"time_s", "distance_m"}.issubset(df.columns):
        raise ValueError(f"CSV {path} hat nicht das erwartete Format")

    df = df.sort_values("time_s").reset_index(drop=True)
    df = df[df["time_s"] <= T_MAX]

    if len(df) < 2:
        print(f"{path}: zu wenige Datenpunkte – übersprungen")
        continue

    # -------------------------------
    # GESCHWINDIGKEIT (0 → T_MAX)
    # -------------------------------
    s0 = df["distance_m"].iloc[0]
    s1 = df["distance_m"].iloc[-1]
    t0 = df["time_s"].iloc[0]
    t1 = df["time_s"].iloc[-1]

    v_ms = (s1 - s0) / (t1 - t0)
    velocities_ms.append(v_ms)

    dataframes.append(df)

if len(dataframes) == 0:
    raise RuntimeError("Keine gültigen CSV-Dateien")

velocities_ms = np.array(velocities_ms)

# ==========================================================
# STATISTIK
# ==========================================================
v_mean = velocities_ms.mean()
v_std  = velocities_ms.std(ddof=1)

print("\n===================================")
print(f"Geschwindigkeit (0 – {T_MAX} s)")
print("===================================")
for i, v in enumerate(velocities_ms, start=1):
    print(f"Run {i:02d}: {v:.3f} m/s = {v*3.6:.2f} km/h")

print("-----------------------------------")
print(f"Mittelwert:        {v_mean:.3f} m/s = {v_mean*3.6:.2f} km/h")
print(f"Standardabweichung {v_std:.3f} m/s = {v_std*3.6:.2f} km/h")
print("===================================")

# ==========================================================
# GEMEINSAME ZEITACHSE
# ==========================================================
t_min = max(df["time_s"].min() for df in dataframes)
t_max = min(df["time_s"].max() for df in dataframes)

time_common = np.linspace(t_min, t_max, 1000)

# ==========================================================
# INTERPOLATION
# ==========================================================
distances_interp = []

for df in dataframes:
    dist_i = np.interp(
        time_common,
        df["time_s"].values,
        df["distance_m"].values
    )
    distances_interp.append(dist_i)

distances_interp = np.array(distances_interp)

# ==========================================================
# MITTELWERT DISTANZ
# ==========================================================
distance_mean = distances_interp.mean(axis=0)

# ==========================================================
# PLOT 1: DISTANZ ÜBER ZEIT
# ==========================================================
plt.figure(figsize=(8, 5))

for dist_i in distances_interp:
    plt.plot(
        time_common,
        dist_i,
        color="gray",
        alpha=0.3,
        linewidth=1
    )

plt.plot(
    time_common,
    distance_mean,
    color="black",
    linewidth=2.5,
    label="Average"
)

plt.xlabel("Time / s")
plt.ylabel("Distance / m")
plt.title(f"Distance over time (n = {len(dataframes)})\n"
          r"$v_{\mathrm{desired}} = 25\,\mathrm{km/h} \equiv 6.944\,\mathrm{m/s}$")
plt.xlim(0, T_MAX)
plt.ylim(bottom=0)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ==========================================================
# PLOT 2: GESCHWINDIGKEIT SCATTER
# ==========================================================
plt.figure(figsize=(7, 4))

x = np.arange(1, len(velocities_ms) + 1)

plt.scatter(x, velocities_ms, s=20, color="black")
plt.axhline(
    v_mean,
    color="black",
    linestyle="--",
    linewidth=1.5,
    label="Average"
)

plt.xticks(x)
plt.xlabel("Measurement")
plt.ylabel("Velocity / m/s")
plt.title(
    f"Velocity distribution (n = {len(dataframes)})\n"
    r"$v_{\mathrm{desired}} = 25\,\mathrm{km/h} \equiv 6.944\,\mathrm{m/s}$")
plt.xlim(0, len(velocities_ms) + 1)
plt.ylim(bottom=5.5, top=8)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()











#---------------------------------------------------------









T_MAX = 0.045   # Sekunden (HIER ANPASSEN)


# ==========================================================
# CSV-DATEIEN (HIER DEFINIEREN)
# ==========================================================
CSV_FILES = [
    "Videos/15_45_1_undistorted.csv",
    "Videos/16_45_2_undistorted.csv",
    "Videos/17_45_3_undistorted.csv",
    "Videos/18_45_4_undistorted.csv",
    "Videos/19_45_5_undistorted.csv",
    "Videos/20_45_6_undistorted.csv",
    "Videos/21_45_7_undistorted.csv",
    "Videos/22_45_8_undistorted.csv",
    "Videos/23_45_9_undistorted.csv",
    "Videos/24_45_10_undistorted.csv",
    "Videos/25_45_11_undistorted.csv",
    ]

# ==========================================================
# CSVs LADEN UND BESCHNEIDEN
# ==========================================================
dataframes = []
velocities_ms = []

for path in CSV_FILES:
    df = pd.read_csv(path)

    if not {"time_s", "distance_m"}.issubset(df.columns):
        raise ValueError(f"CSV {path} hat nicht das erwartete Format")

    df = df.sort_values("time_s").reset_index(drop=True)
    df = df[df["time_s"] <= T_MAX]

    if len(df) < 2:
        print(f"{path}: zu wenige Datenpunkte – übersprungen")
        continue

    # -------------------------------
    # GESCHWINDIGKEIT (0 → T_MAX)
    # -------------------------------
    s0 = df["distance_m"].iloc[0]
    s1 = df["distance_m"].iloc[-1]
    t0 = df["time_s"].iloc[0]
    t1 = df["time_s"].iloc[-1]

    v_ms = (s1 - s0) / (t1 - t0)
    velocities_ms.append(v_ms)

    dataframes.append(df)

if len(dataframes) == 0:
    raise RuntimeError("Keine gültigen CSV-Dateien")

velocities_ms = np.array(velocities_ms)

# ==========================================================
# STATISTIK
# ==========================================================
v_mean = velocities_ms.mean()
v_std  = velocities_ms.std(ddof=1)

print("\n===================================")
print(f"Geschwindigkeit (0 – {T_MAX} s)")
print("===================================")
for i, v in enumerate(velocities_ms, start=1):
    print(f"Run {i:02d}: {v:.3f} m/s = {v*3.6:.2f} km/h")

print("-----------------------------------")
print(f"Mittelwert:        {v_mean:.3f} m/s = {v_mean*3.6:.2f} km/h")
print(f"Standardabweichung {v_std:.3f} m/s = {v_std*3.6:.2f} km/h")
print("===================================")

# ==========================================================
# GEMEINSAME ZEITACHSE
# ==========================================================
t_min = max(df["time_s"].min() for df in dataframes)
t_max = min(df["time_s"].max() for df in dataframes)

time_common = np.linspace(t_min, t_max, 1000)

# ==========================================================
# INTERPOLATION
# ==========================================================
distances_interp = []

for df in dataframes:
    dist_i = np.interp(
        time_common,
        df["time_s"].values,
        df["distance_m"].values
    )
    distances_interp.append(dist_i)

distances_interp = np.array(distances_interp)

# ==========================================================
# MITTELWERT DISTANZ
# ==========================================================
distance_mean = distances_interp.mean(axis=0)

# ==========================================================
# PLOT 1: DISTANZ ÜBER ZEIT
# ==========================================================
plt.figure(figsize=(8, 5))

for dist_i in distances_interp:
    plt.plot(
        time_common,
        dist_i,
        color="gray",
        alpha=0.3,
        linewidth=1
    )

plt.plot(
    time_common,
    distance_mean,
    color="black",
    linewidth=2.5,
    label="Average"
)

plt.xlabel("Time / s")
plt.ylabel("Distance / m")
plt.title(f"Distance over time (n = {len(dataframes)})\n"
          r"$v_{\mathrm{desired}} = 45\,\mathrm{km/h} \equiv 12.5\,\mathrm{m/s}$")
plt.xlim(0, T_MAX)
plt.ylim(bottom=0)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ==========================================================
# PLOT 2: GESCHWINDIGKEIT SCATTER
# ==========================================================
plt.figure(figsize=(7, 4))

x = np.arange(1, len(velocities_ms) + 1)

plt.scatter(x, velocities_ms, s=20, color="black")
plt.axhline(
    v_mean,
    color="black",
    linestyle="--",
    linewidth=1.5,
    label="Average"
)

plt.xticks(x)
plt.xlabel("Measurement")
plt.ylabel("Velocity / m/s")
plt.title(
    f"Velocity distribution (n = {len(dataframes)})\n"
    r"$v_{\mathrm{desired}} = 45\,\mathrm{km/h} \equiv 12.5\,\mathrm{m/s}$")
plt.xlim(0, len(velocities_ms) + 1)
plt.ylim(bottom=11, top=13)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()















#---------------------------------------------------------












# ==========================================================
# EINSTELLUNG: MAXIMALE ZEIT
# ==========================================================
T_MAX = 0.04   # Sekunden (HIER ANPASSEN)


# ==========================================================
# CSV-DATEIEN (HIER DEFINIEREN)
# ==========================================================
CSV_FILES = [
    "Videos/26_55_1_undistorted.csv",
    "Videos/27_55_2_undistorted.csv",
    ]

# ==========================================================
# CSVs LADEN UND BESCHNEIDEN
# ==========================================================
dataframes = []
velocities_ms = []

for path in CSV_FILES:
    df = pd.read_csv(path)

    if not {"time_s", "distance_m"}.issubset(df.columns):
        raise ValueError(f"CSV {path} hat nicht das erwartete Format")

    df = df.sort_values("time_s").reset_index(drop=True)
    df = df[df["time_s"] <= T_MAX]

    if len(df) < 2:
        print(f"{path}: zu wenige Datenpunkte – übersprungen")
        continue

    # -------------------------------
    # GESCHWINDIGKEIT (0 → T_MAX)
    # -------------------------------
    s0 = df["distance_m"].iloc[0]
    s1 = df["distance_m"].iloc[-1]
    t0 = df["time_s"].iloc[0]
    t1 = df["time_s"].iloc[-1]

    v_ms = (s1 - s0) / (t1 - t0)
    velocities_ms.append(v_ms)

    dataframes.append(df)

if len(dataframes) == 0:
    raise RuntimeError("Keine gültigen CSV-Dateien")

velocities_ms = np.array(velocities_ms)

# ==========================================================
# STATISTIK
# ==========================================================
v_mean = velocities_ms.mean()
v_std  = velocities_ms.std(ddof=1)

print("\n===================================")
print(f"Geschwindigkeit (0 – {T_MAX} s)")
print("===================================")
for i, v in enumerate(velocities_ms, start=1):
    print(f"Run {i:02d}: {v:.3f} m/s = {v*3.6:.2f} km/h")

print("-----------------------------------")
print(f"Mittelwert:        {v_mean:.3f} m/s = {v_mean*3.6:.2f} km/h")
print(f"Standardabweichung {v_std:.3f} m/s = {v_std*3.6:.2f} km/h")
print("===================================")

# ==========================================================
# GEMEINSAME ZEITACHSE
# ==========================================================
t_min = max(df["time_s"].min() for df in dataframes)
t_max = min(df["time_s"].max() for df in dataframes)

time_common = np.linspace(t_min, t_max, 1000)

# ==========================================================
# INTERPOLATION
# ==========================================================
distances_interp = []

for df in dataframes:
    dist_i = np.interp(
        time_common,
        df["time_s"].values,
        df["distance_m"].values
    )
    distances_interp.append(dist_i)

distances_interp = np.array(distances_interp)

# ==========================================================
# MITTELWERT DISTANZ
# ==========================================================
distance_mean = distances_interp.mean(axis=0)

# ==========================================================
# PLOT 1: DISTANZ ÜBER ZEIT
# ==========================================================
plt.figure(figsize=(8, 5))

for dist_i in distances_interp:
    plt.plot(
        time_common,
        dist_i,
        color="gray",
        alpha=0.3,
        linewidth=1
    )

plt.plot(
    time_common,
    distance_mean,
    color="black",
    linewidth=2.5,
    label="Average"
)

plt.xlabel("Time / s")
plt.ylabel("Distance / m")
plt.title(f"Distance over time (n = {len(dataframes)})\n"
          r"$v_{\mathrm{desired}} = 55\,\mathrm{km/h} \equiv 15.277\,\mathrm{m/s}$")
plt.xlim(0, T_MAX)
plt.ylim(bottom=0)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ==========================================================
# PLOT 2: GESCHWINDIGKEIT SCATTER
# ==========================================================
plt.figure(figsize=(7, 4))

x = np.arange(1, len(velocities_ms) + 1)

plt.scatter(x, velocities_ms, s=20, color="black")
plt.axhline(
    v_mean,
    color="black",
    linestyle="--",
    linewidth=1.5,
    label="Average"
)

plt.xticks(x)
plt.xlabel("Measurement")
plt.ylabel("Velocity / m/s")
plt.title(
    f"Velocity distribution (n = {len(dataframes)})\n"
    r"$v_{\mathrm{desired}} = 55\,\mathrm{km/h} \equiv 15.277\,\mathrm{m/s}$")
plt.xlim(0, len(velocities_ms) + 1)
plt.ylim(bottom=14.5, top=16.5)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
