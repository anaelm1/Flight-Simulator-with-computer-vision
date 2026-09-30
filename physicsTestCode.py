#trying to test out physics stuff I js learned 
from ursina import *
app = Ursina()

#Global stuff:
m = 1 #kg
g = 9.81 #m/s^2
v = Vec3(0, 0, 0)
k = 3 #drag coefficient. This needs to be calculated but Im using a random value of 0.3 rightnow 
T = 0.0 #Thrust level

plane = Entity(model='plane', scale=(20,1,20), color=color.green)

camera.position = (0, 5, -20)
camera.rotation_x = 10

drone = Entity(model='cube', color=color.orange)
drone.mass = m

def update():
    global T, v #Global variables are required to be declared inside the func
    #Here will be the physics implementation

    thrust_rate = 10
    pitch_speed = 60.0
    roll_speed = 60.0
    yaw_speed = 40.0

    #Thrust control
    T += held_keys["space"] * time.dt * thrust_rate
    T -= held_keys["shift"] * time.dt * thrust_rate
    T = clamp(T, 0, 20)

    drone.rotation_x += pitch_speed * time.dt * held_keys['w']
    drone.rotation_x -= pitch_speed * time.dt * held_keys['s']

    drone.rotation_z += roll_speed * time.dt * held_keys['a']
    drone.rotation_z -= roll_speed * time.dt * held_keys['d']

    drone.rotation_y -= yaw_speed * time.dt * held_keys['q']
    drone.rotation_y += yaw_speed * time.dt * held_keys['e']
        
    
    #Forces calculation
    f_gravity = Vec3(0, -drone.mass * 9.81, 0)
    f_thrust = drone.up * T #thrust and drag apply in all directions that's why
    f_drag = -v * k         #they will be added universally while gravity is only for down
    f_net = f_thrust + f_gravity + f_drag

    #We will use acceleration to get velocity 
    acceleration = f_net/ drone.mass #f = ma
    v += acceleration * time.dt #Eular Numerical part 
    drone.position += v * time.dt #Eular Numerical part 
    print(v)

    #if it collides with the ground
    if drone.y < 0:
        drone.y = 0
        v = Vec3(0, 0, 0)

app.run() 