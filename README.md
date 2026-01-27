# SpinLauncher

## Project Overview
The SpinLauncher is a mechanical puck launching system designed to accelerate an ice hockey puck using centrifugal force. A rotating arm generates controlled launch velocities, allowing different puck speeds to be set reproducibly. In addition to linear speed control, the system enables the generation of puck spin, which is relevant for realistic shot simulation.

The primary goal of the SpinLauncher is to produce repeatable and well-defined hockey shots. The system was developed as an extension and improvement of the shooting device used in the master’s thesis “Hockey Pro”, which aimed to generate reproducible shots for a camera-based ice hockey shooting training system.

The SpinLauncher project was carried out as a student project within the Master’s program (MST) during the Winter Semester 2025/2026.

## System Concept & Principle
The core mechanical concept of the SpinLauncher is a horizontally rotating arm driven by an electric motor. Two standard ice hockey pucks are mounted at opposite ends of the arm. This symmetric configuration ensures dynamic balance during rotation, significantly reducing vibrations and mechanical stress on the system.

During operation, both pucks are accelerated simultaneously and experience identical centrifugal forces. The system is designed for bidirectional release, meaning that the mechanical release principle is implemented on both sides of the rotating arm. In experimental operation, however, only one puck is used for measurement, while the second puck is safely intercepted. This approach preserves balance.

By adjusting the rotational speed of the arm, the launch velocity of the puck can be precisely controlled. The combination of symmetric mass distribution and controlled release enables reproducible shot conditions and stable system behavior.

## Hardware Setup
The SpinLauncher hardware consists of a mechanically simple but dynamically balanced rotating system. The central component is a rigid wooden arm with a total diameter of approximately 80 cm, mounted horizontally and driven by an electric motor. The geometry and dimensions of the rotating arm are defined in the CAD model [`/drawings`](./drawings).

Two standard ice hockey pucks are mounted at opposite ends of the rotating arm. This symmetric mass distribution ensures dynamic balance during operation and significantly reduces vibrations at higher rotational speeds. The puck holders and integrated release mechanisms are defined in
['/release Mechanism'](./release Mechanism). and the corresponding part files in the same directory.

The electronic components required for motor control and sensor feedback are documented in the ['/Electronic'](.Electronic) directory. This folder contains the complete circuit schematic, including the motor drive, power supply, and the Hall effect sensor used for rotational speed measurement.

The rotating arm is connected to the motor shaft via a custom-designed coupling, which ensures reliable torque transmission while maintaining axial alignment. All rotating components are mounted on a rigid frame structure that supports the motor and ensures a stable horizontal rotation axis. The frame design, including mounting points for the motor and safety elements, is defined in [`/drawings`](./drawings).

## Control & Software
The SpinLauncher is controlled via a software-based speed control system that enables precise and reproducible adjustment of the launcher’s rotational velocity. The rotational speed of the arm is measured in real time using a Hall effect sensor, which detects the rotation of the motor shaft and provides feedback in the form of pulses. From these pulses, the system continuously calculates the current rotational speed in revolutions per minute (RPM).

The measured RPM is used to monitor the acceleration process and to verify that the predefined target speed has been reached. This feedback mechanism allows reliable speed setting and ensures that launches are performed only under well-defined conditions.

All control-related code is located in the ['/SpinlaunchController'](./SpinlaunchController) directory of this repository.

In addition to the embedded control logic, a web-based control interface is implemented directly on the controller. The system hosts a lightweight web server that allows the user to:
- set target RPM values,
- monitor the current rotational speed,
- manually trigger the puck release.

The release can be initiated via the web interface once the system has reached the predefined target RPM and angular position. This ensures that the puck is released only when both speed and orientation conditions are satisfied, improving repeatability and experimental control.

The modular structure of the control software allows easy modification of speed thresholds, angular conditions, and trigger logic. This design enables future extensions, such as automated release criteria, closed-loop speed control, or integration of additional sensor feedback.

## Experimental Setup & Test Procedure

### Experimental Setup

All experiments were conducted using a controlled laboratory setup designed to ensure reproducible launch and measurement conditions. The SpinLauncher was mounted on a rigid frame, and all measurements were performed under identical mechanical, camera, and lighting conditions.

High-speed recordings were acquired using a visually triggered camera system operating in an image-based auto-trigger mode. Image sequences were recorded before and after puck launch to capture the complete release event. The camera was positioned perpendicular to the puck trajectory, facing a calibrated checkerboard plane.

The camera configuration was identical for all experiments and is summarized below:

- **Frame rate:** 3200 fps  
- **Exposure time (shutter speed):** 310 µs  
- **Sensor resolution:** 1280 × 800 pixels  
- **Bit depth:** 12 bit  
- **Lens:** Fixed-focus lens, focal length 25 mm  
- **Distance between camera lens and checkerboard plane:** 52.5 cm  
- **Trigger mode:** Image-based auto-triggering based on grayscale intensity changes  
- **Recording duration:** approx. 0.09 s pre-trigger and 0.55 s post-trigger  

Images of the complete experimental setup, including camera placement and launcher orientation, are provided in the [`/pictures`](./pictures) directory.


### Test Procedure

The SpinLauncher was tested at multiple predefined target velocities. For each target speed, the launcher was accelerated to the corresponding rotational speed before the puck release was manually triggered.

The following test conditions were investigated:

- **25 km/h (≈ 166 RPM):** 11 repetitions  
- **45 km/h (≈ 299 RPM):** 11 repetitions  
- **55 km/h (≈ 365 RPM):** 2 repetitions  

The number of repetitions at 55 km/h was limited due to **mechanical failure of the system**, which resulted in damage to the launcher and prevented further testing at this speed.

All measurement data, including raw results and processed values, are stored in the [`/Measurements/V2`](./Measurements/V2) directory. This folder contains:
- recorded measurement data,
- analysis scripts,
- and the corresponding Excel files that logged the test run. 

The software and data provided in this repository allow full traceability of the experimental procedure and results presented in the paper and presentation.


## Data & Analysis

The recorded measurement data were processed and analyzed to evaluate the launch velocity and repeatability of the SpinLauncher. All raw data and processed results are stored in the [`/Measurements/V2`](./Measurements/V2) directory.

Launch velocities were determined based on image sequences recorded with the high-speed camera. The puck position was extracted frame by frame using a **custom Python analysis script**, and the displacement over time was used to calculate the translational velocity after release. Only frames in which the puck had fully disengaged from the launcher were considered for evaluation.

For each target speed, multiple repetitions were analyzed to assess repeatability. Mean values and variations of the measured launch velocities were calculated and used to compare the achieved performance across different operating points. The resulting values form the basis for the plots and tables presented in the presentation and paper.

The Python script used for data processing is provided in the [`/Measurements/V2`](./Measurements/V2) directory. All analysis steps are documented and can be reproduced or extended by future users.


## Results Summary

The SpinLauncher demonstrated reliable and reproducible performance across the tested velocity range. For target speeds of **25 km/h** and **45 km/h**, the system achieved stable operation with consistent launch conditions over **11 repeated trials** each. The measured launch velocities showed low variation between repetitions, indicating good repeatability of the centrifugal acceleration and release mechanism.

At higher target speeds, the system approached its mechanical limits. Tests at **55 km/h** were successfully performed for **two repetitions**, confirming the feasibility of higher launch velocities in principle. However, subsequent testing at this speed was discontinued due to mechanical failure of the launcher, which resulted in damage to the system. This failure highlights the increasing structural and dynamic loads acting on the rotating components at elevated rotational speeds. In addition, the response time of the release mechanism was insufficient at higher rotational speeds, leading to delayed puck disengagement and contributing to the observed mechanical failure.

All raw and processed measurement data supporting these results are stored in the [`/Measurements/V2`](./Measurements/V2) directory. This folder contains the complete dataset used for analysis, including measurement files, evaluation scripts, and plots.

Overall, the results confirm that the SpinLauncher is well suited for generating reproducible puck launches within a moderate speed range. The experimental data further provide valuable insight into the mechanical limitations of the current design and define clear boundaries for safe and reliable operation.


## Limitations and Future Work

The current SpinLauncher design exhibits several limitations that became apparent during high-speed testing and provide clear directions for future improvements.

One key limitation is the performance of the release mechanism. At elevated rotational speeds, the response time of the current mechanism is insufficient, leading to delayed puck disengagement. Future work should focus on improving the release dynamics to ensure reliable operation at higher RPMs. In particular, the use of a linear pin actuator with sufficient pulling force should be considered as an alternative to the currently used servo-based solution.

Another limitation concerns the structural stiffness of the rotating arm. At higher rotational speeds, the arm exhibited noticeable deflection, causing parts of the rotating assembly to come into contact with surrounding components. This indicates that the arm stiffness is insufficient for operation at higher loads. Future iterations should therefore include structural reinforcement of the rotating arm or the use of stiffer materials.

A further limitation is the limited control and quantification of puck spin. While spin is generated implicitly by the launcher, it is neither independently adjustable nor directly measured. A potential approach to influence puck spin is to vary the launching angle, which may allow controlled manipulation of rotational behavior. In principle, the high-speed camera recordings acquired during the experiments provide sufficient data to extract and analyze puck spin. However, no dedicated analysis or systematic investigation of spin effects has been conducted so far.

Safety is another important aspect that requires improvement. In the current setup, the second puck mounted on the rotating arm remains in motion after the primary puck is released. As a concrete future improvement, the unused puck should be intercepted immediately at the launcher exit using a dedicated catching or deflection mechanism. This would significantly reduce the risk associated with uncontrolled puck motion and improve the overall safety of the system.

Addressing these limitations is expected to increase the maximum achievable launch speed while improving reliability, experimental control, and operational safety.


## Further Documentation
Paper:

Notion: https://www.notion.so/mci-medtech/Hockey-PRO-28091a52c19480998451c0e8b286c635
