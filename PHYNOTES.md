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
