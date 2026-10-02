## Physics Notes 
I dsicussed the topic with Gemini and in order to make this I would also need to know some physics equations. 
This is the list of equations: 
1. Force Balance
2. Gravity Force
3. Thrust Vector 
5. Linear Air Resister (Drag)
6. Eular Numerical Integration step

I don't know any of this and Gemini is helping me in the study part. 

# First article 

In a quadcopter, there are 4 equally spaced rotors so a swashplate mechanism is NOT needed (the device which controls inputs like speed of the motors)

In total there are 6 degrees of freedom: 3 translational and 3 rotational (x, y, z)

Roll: clockwise anticlockwise X - axis
Pitch: up down Y - axis
Yaw: left to right Z - axis 

1. Coordinates 
Forces are calculated in 2 coordinate systems. 
    1. Inertial frame (world frame): fixed ground reference. Positions are in form of 3d vectors x = [x, y, z]^T and gravity pulls down straight along the -z axis that will be [0, 0, -g]^T. 
    2. Body Frame: Fixed to the drone's center of mass. It is for the rotors who initially point at +z axis.

We now need to convert the drone forces like each motors thrust into the world frame. For this a Rotational matric (R) is used. It has the angles of roll pitch yaw

The equation looks like this: (Can't copy) but basically it is a sin and cos 3d vector where we put the angles for each of the 3 rotational axis. 

2. Translational Dynamics (Linear Acceleration)
Works on f=ma
    1. Each rotor has a vertical thurst force which is propotional to the square of its angular motor velocity w (rate at which a motor's shaft rotates). This is the equation: F = k * w^2
    2. Summing up the thrust of all 4 rotors gives this equation: T = k(w^2,w^2, w^2, w^2)
    3. And this T looks smthg like this in the body frame (0, 0, T). 
    4. Now we take the R from the last heading and mutply with the Thrust vector gives us the vector on how the drone accelerates in the real world. 
    5. Summming up all the force vectors in the world frame: force net = force thrust + force gravity + force drag. Gravity drag are negative and opposite direction with formulas of their own but I am not writing them. 
    6. The 3 axis vector can then be divided into the 3 parts. 

3. Rotational Dynamics 
In order to rotate, the drone relies on difference in individual motor speeds. These are the 4 rotors. 
Rotor 1: Front (counter clockwise)
Rotor 2: Right (Clockwise)
Rotor 3: Back (Counter clockwise)
Rotor 4: Left (clockwise)

Torque is kinda like turning effect. 
1. Roll Torque (x): difference between left and right motor thrusts.
2. Pith Torque (y): difference between backa nd front motor thrusts.
3. Yaw Torque (z): Spinning the propellers causes torque onto the frame (newtons 3rd law). Counter-clockwise rotors produce clockwise torque, and vice versa

Angular Acceleration: how fast the drone's spin rate is changing. 
Eg if the left motor pushes harder than the right motor then the drone's left side lifts and there is +Tx thrust. Also the formulas for these use L which is arm length. But yaw torque uses newtow's 3rd law where if we speed the front 2 motors up they will cause the frame to tilt downwars. That's why in hover all4 motors spin at equal speeds. 

Moment of inertia (I): This tells how hard is it to rotate an object. This resistance is formatted as a 3 x 3 matrix. 

Eular's equation: This is f = ma but for 3d spinning objects with one extra term of gyroscopic effect. In 2d, f=ma works but in 3d it doesn't as the object is already sppining in 3D space. The equation is Torque = rotational acceleration + Gyroscopic resistance. In aggressive maneuvers where the drone is already spinning, we use this to make sure the existing spin velocity w and angular momentum work together. 

# stuff gemini said I missed
1. Gravity force: This is the gravity equatin: f = (0, 0, -mg). Uses the w=mg formula 
2. Drag: (-kdrag.vx, -kdrag.vy, -kdrag.vz) Kdrag is the linear drag coeffient 
3. Eular Numerical Integration step: these are the equation for updating velocity and positions each frame. 
linear acceleration = fore net/mass
Velocity at time t = velocity + linear acceleration * change in time
position at time t = position t + velocity at time t * change in time


IMP NOTE:i js found out that in this paper z is up but in urina y will be up so I will need to keep that in mind. 

## Conclusion of this
I have coded a file called physicsTestCode. It has the actualy calculations that I will need to do. 
The sequence, in my own words, is:
    1. Calculate force of gravity using w = mg 
    2. Calculate force of thrust by drone up vector and thrust value 
    3. Calculate force of drag by -v * drag coefficent 
    4. Use all 3 to calculate net force 
    5. Get acceleration using f = ma
    6. Get velocity using acceleration * time 
    7. Finally get drone position by adding distance moved (velocity * time) into the drone vector  

About pitch, roll, yaw: Angular velocity should be used instead of direct keys as in real life the drone won't just stop and will instead slowly come to stop. For now I have added basic key press rotation which works cuz we are using drone.up whhich includes the new direction.  

Angular Vecocity: 
It is same as linear except different variables. It is defined as the ratio of angular displacement to time taken.
position turns into angle 
linear velocity turns into angular velocity 
force turns into torque
mass turns into moment of intertia 
linear drag turns into rotational drag

Steps for it:
1. Calculate torque from eacha axis 
2. Calcualte rotational drag whic is k_rot = linear drag x angular velocity 
3. Calculate net torque by adding both 
4. Caculate angualr acceleration which is torque/moment of inertia (same as f=ma)
5. Update angular velocity which is old velocity + (acceleration x delta t)
6. update rotation angle wwhich is old angle + (new velocity x delta t)

Torque = distance from pivot * force * sin(angle betweeen force and lever arm)
but gemini instead is telling me to just increment on key presses etc. 

k_rot = torque / max angular velocity

Moment of intertia (I): This is like the mass for rotations. It has a formula for each axis which uses mass, width, height, depth. 
I_x = 1/12 * m * (h^2 + d^2) 
I_y = 1/12 * m * (w^2 + d^2) 
I_z = 1/12 * m * (w^2 + h^2) 

IMP SHIT: Ursina calculates in deg while the formulas use radians so I need to change. 

I have so far implemented the base system which is extremely sensitive and making it hard for me to control. That's why an active flight controller (stabilization system) is needed. 

## Stabilization system:
I will do stabilization using angle mode. In this, we change our keys from how fast the drone spins (raw physics) to what angle does the drone tilt.

This is the current system:
if we press W, the drone will pitch forward and spin faster and faster
when we release, the  torque increment stops but the drone still stays tilted

It works like this:
if we press W, the drone will tilt forward at an angle and hold it
when we will release, the angle will go back to 0 
This works like a rubber band

Steps to do:
1. Get angles and use to find the angle of error meaning where the difference between the where the drone wants to be and where it currently is. 
target angle = key input * max tilt angle (can be any degrees)
angle error = target angle -  current angle
2. Calculate the correction torque by error angle * P. P is a strength factor which makes it harder for the drone to tilt so that it doesn't slam.
3. Add damping by final torque = correction torque - (angular velocity * damping coefficent).

Also in this the yaw is not included cuz we always wanna see the drone be top facing when we are not doing anything. 
For yaw, I wil add a head-locking controller. In this, if the yaw keys are pressed it will tilt but if not then it will calculate shortest angular distance between target (always be 0) and current target and apply it on the torque. So, in this way the drone will straighten out. We are using trigonometry to calculate the distance and its just copy paste. 

I tried writting a soft landing code but Im gonna leave it in todo. 
 
## 4 rotor motor physics
The next step is to split the thrust in 4 individual motors. The flight controller needs to calculate each motors commands so that they naturally produce the thrust, pitch, roll, yaw. 

Motor 1 (rear right) spins CW 
Motor 2 (front right) spins ACW
motor 3 (rear left) spins ACW
motor 4 (front left) spins CW    

To keep the drone from spinning in circles, two motors spin CW and two spin ACW.

## Lets first study about the physics of each rotor:
Each motor has a rotationl speed (rad/s)
It generates 2 outputs from the square of this speed 
1. Aerodynamic Thrust Force: k * rotationl speed^2 (This pushes the drone upwards)
2. Reaction Drag Torque: k * rotational speed^2 (Due to Newton's third law, when we spin the propeller it produes a counter torque in the opposite direction)
(k is the thrust coefficient and K is the is moment coefficient)

I should make a function of the flight controller. It will input the desired total thrust and desired axis torques and then split it into the 4 motor forces.
The formula goes smthg like this:

d is the distance from center to arm along each axis. 
d = L/underroot(2)
but for y axis (yaw) it isn't needed beacuse it works on counter torque balance CW and ACW motors 

cq is the torque to thrust ratio calculated by k/k (first is moment second is thrust). torque one will be smaller cuz it measures the drag. 


The sign change depending on the motors position 
F1 = T/4 + torquex/4d - torquez/4d + torquey/4cq
F2 = T/4 - torquex/4d - torquez/4d - torquey/4cq
F3 = T/4 + torquex/4d + torquez/4d - torquey/4cq
f4 = t/4 - torquex/4d + torquez/4d + torquey/4cq

RMP spin latency: Electric motros can't change their RPM (revolutions per minute) instantly due to rotor intertia. We add that lag with a constant time (0.03 s) but for the inertia one we use this formula:
motor acceleration rate = (target speed - current speed) / motor time constant
In python we will use this one:
motor speed += ((cmd_speed - motor_speed) / motor_time_constant) * time.dt

cmd_speed is target speed requested by controller       
motor_soeed is actual speed
Speed error is calculated by both
motor_time_constant is lag 
This formula will allow the rpm to increase exponentially when needed otherwise slowly 

## Enivronmental physics
I now need to add environmental variables
1. drag: This will oppose the final velocity. 
relative velocty = drone velocity - wind velocity 
wind velocity will be 
2. Body drag eqn: -0.5p * Cd * A * |relative v| * relative v
p is air density, 1.225 kg/m3
Cd is drag coefficent 
A is cross sectional area
3. Wind velocity = steady velocity + gust velocity + turbulence velocity 
steady velocity will be constant. smtg like 5 m/s facing east
gust velocity will be periodic igh intensity force burst. We will use 1 - cosine for this. 
The formual is: gust at time t = (max gust intensity/2)(1 - cos(2pi*t/T))
t is time elapsed since gust started
T is total gust duration

turbulence velocity will be chaotic high freq changes. Will use standard aerospace models like the dryden turbulene model (don't know what that is yet)

Last thing: Air density will scale from both thrust and torque drag.
thrust/(thrust cofficient * anguar velocity^2) = p 
drag torque/(drag cofficient * anguar velocity^2) = p 

In order to implement I will: 
1. Calculate wind velocity first 
2. Calculate relative velocity
3. change current body drag f_drag = -v * k into body drag eqn