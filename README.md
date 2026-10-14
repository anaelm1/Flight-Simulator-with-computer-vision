# Flight Simulator With Computer Vision 
This project is a 3D First Person Drone Simulator built in Python using the Ursina Engine. The second part is autonomous navigation system with computer vision, but I haven't implemented it yet. The hightlight of the project is that everything is done based on physics such as the physical, aerodynamic and environmental forces.  

## Reason for making this project
The eventual goal with going down the Quadcopter rabbit hole is to replicate this exact project in real life. That's why I am making this project to improve my conceptual knowledge of Quadcopters and the physics behind them. Similarly, this project will also be a part of my portfolio as my intended majors (Mechanical Engineering) are closely related. 

## Key Features & Architecture
1. Flight Dynamics:
    - Equations of Motion: Integrates forces and rotational kinematics using Euler numerical integration to update position, linear velocity and angular velocity. 
    - Aerodynamic Drag: Computes translational and rotational drag forces based on dynamic air density, cross-sectional area, and relative airspeed.

2. Electronic Speed Controller:
    - Motor Response Lag: Individual motor speeds are updated with a time lag mimicing real life motors.
    - Ground Effect: Increased Thrust when operating within 1m of the groud mimicking real life. 
    - Desaturation and Limits: Limited Thrust per motor (idle force of 0.15 N up to 20 N, or 32 N during emergencies)
    - Anti Crash Safety Mechanism: Automatically detects high-rate descents near the ground and temporarily overrides motor outputs to maximum thrust to prevent high velocity crash. 

3. Environmental Modeling:
    - Steady Wind: A horizontal wind vector (1.5 m/s) blowing across the map.
    - Dynamic Gusts: Wind gusts using a 1 - cosine curve model with randomized peak speeds, durations and directional angles mimicking real life. 
    - 3D Dryden Turbulence Model: Realistic turbulence model that is also used by the US AirForce. 

4. Control Systems and Navigation
    - Flight Modes:
        - Auto Hover (h): Matches and holds the target altitude using a Proportional-Derivative controller.
        - Yaw & Tilt Stabilization: Smooths orientation using custom  stabilization constants.
    - Waypoint Navigation: A sequence of 3D crosshair targets that cycle automatically when the drone reaches them. Made to mimic deliveries. 

5. Telemetry, UI and Logging: 
    - Dual Camera System: Primary first person camera with a third person display panel that is toggleable via the v key. 
    - HUD Telementry: Real time on screen display tracking thrust, altitude, speed, velocity vectors, active flight modes and waypoint distance. 
    - CSV Data Logging: Automatically records flight telemetry (timestamp, position coordinates, velocity components, thrust level, and system states) to a timestamped CSV file every second.

6. Dynamic Audio: 
    - Rotor Audio: Scales volume with the average RPM of all four motor.
    - Wind Audio: Scales wind audio and pitch with the windspeed.
    - Anti Crash: Automatically raises the alarm volume when the anti crash mechansim engages

## Controls 
- Space/Shift = Increase / Decrease Thrust
- W/S = Pitch Forward / Backward
- A/D = Yaw Left / Right
- Q/E = Roll Left / Right
- H = Toggle Auto Hover Mode
- v = Toggle 3rd Person Viewport
- R = Reset Drone Position

## How to Run Locally

To run this project on your local machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anaelm1/Flight-Simulator-with-computer-vision
   cd Flight-Simulator-with-computer-vision
   ```

2. **Install the required dependencies:**
   ```bash
   pip install ursina numpy
   ```

3. **Run the project:**
   ```bash
   python main.py
   ```

---

## Other Details
- All physics equation gand Ursina details are documented the in the notes.md, and show the learning process behind each line of code. 
- This project is half way done, and I am actively working on the second part i.e automation/computer vision
- This project is being made in Hack Club Phantom. 