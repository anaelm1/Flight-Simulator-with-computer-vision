# Flight Simulator With Computer Vision 
This project is a 3D First Person Drone Simulator built in Python using the Ursina Engine. The second part is autonomous navigation system with computer vision, but I haven't implemented it yet. The hightlight of the project is that everything is done based on actual physics equations such as the physical, aerodynamic and environmental forces.  

## Reason for making this project
The eventual goal with going down the Quadcopter rabbit hole is to replicate this exact project in real life. That's why I am making this project to improve my conceptual knowledge of Quadcopters and the physics behind them. Similarly, this project will also be a part of my portfolio as my intended majors (Mechanical Engineering) are closely related. 

## Features 
1. Flight Basics:
    - It uses kinematics equations of motion to calculate the linear and angular velocities (Eular's method).
    - It calculates drag forces based on a number of factors like air density (decreases with altitude), relative airspeed etc.

2. Electronic Speed Controller:
    - The ESC mimics real life motors lag response.
    - There is increased Thrust when the droen is in 1m of the groud mimicking real life (Ground effect).
    - Each motor has a limited thrust (idle force of 0.15 N up to 20 N or 32 N during emergencies).
    - It also has an Anti Crash Safety Mechanism which automatically detects high speed falls near the ground and to save the drone temporarily increases motor outputs to maximum thrust.

3. Environmentals:
    - A constant wind of 1.5 m/s is present on the map.
    - There are wind gusts as well which use a 1 - cosine curve model with all quantities (angle, speed, duration) randomized. 
    - I also coded the 3D Dryden Turbulence Model which is a realistic turbulence model that is also used by the US AirForce. 

4. Other things:
    - Auto Hover: If you press the "H" key, the drone locks in at the current altitude using a PD controller.
    - I have setup a basic waypoint game where you have to fly the drone to a series of randomized targets on the map. It is made to mimic deliveries. 
    - There is a dual camera system with a main first person camera and a third person display panel that is controlled using the "V" key. 
    - I also added a screen on the left side which shows basic details (in real time) about the drone like thrust, altitude, speed, velocity vectors, waypoint distance etc. 
    - The app also automatically records flight data to a CSV file every second.

7. Dynamic Audio: 
    - The volume of the rotor increases as the RPM of the motors increase.
    - The pitch and volume of the wind increases as the overall wind speed (including gusts and turbulence as well) increases. Due to this, the wind audio is more clear as the drone goes higher.
    - It raises the alarm volume when the anti crash mechansim engages.

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

## AI Usage
Gemini was used for research purposes, debugging and sometimes code snippets. No direct copypasting without understanding the code first.

## Other Details
- All physics equation and Ursina details are documented the in the notes.md, and show the learning process behind each line of code. 
- This project is half way done, and I am actively working on the second part i.e automation/computer vision
- This project is being made in Hack Club Crossroads. 
