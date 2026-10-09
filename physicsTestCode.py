#trying to test out physics stuff I js learned 
from ursina import *
app = Ursina()
import math 

#keeps the angles between -180 and 180
def angleRange(angle):
    return (angle + 180) % 360 - 180 

#Global Variables:
m = 1 #kg
g = 9.81 #m/s^2
v = Vec3(0, 0, 0)
Ang_v_RAD = Vec3(0, 0, 0) # rad/s . angular velocity 

k = 0.3 #drag coefficient. Random Value for now
T = 0.0 #Thrust level
L = 0.1 #m .Arms length.
d = L/math.sqrt(2) #prependicular arm distance to the x and z axis
k_thrust = 1 #thrust coefficient. Random value for now 
k_torque = 0.02 #torque coefficent. Random value for now 
k_motordrag = 0.1 #Motor drag coefficent. Random value for now 
motor_responsetime = 0.02 #motor lag . Random value rightnow
motor_speed_array = [0.0, 0.0, 0.0, 0.0] #rad/s for each motor. m1, m2, m3, m4

torque = Vec3(0, 0, 0)
k_drag = 0.3 #rotatinal drag coeefficent.
I_x = 0.167 #Moment of intertia x
I_y = 0.167 #Moment of intertia y
I_z = 0.167 #Moment of intertia z
I = Vec3(I_x, I_y, I_z) #Moment of intertia
torque_applied = Vec3(0, 0, 0)

RAD_TO_DEG = 180.0 / math.pi

P = 8.0 #constant with which we pull towards target angle
D = 1.2 #damping coefficient 
P_yaw = 6.0
D_yaw = 1.0 
max_tilt = math.radians(20.0) #max the drone can tilt to a side
target_yaw_rad = 0.0 #this is the default position of a drone 

#Environmentals
wind_steady_velocity = Vec3(5, 0, 0) #5 m/s horizontal wind blowing from west to east across the map

is_gusting = False
cooldown_timer = 5.0 #seconds before first gust 
active_timer = 0.0 
gust_peak_speed = 0.0
gust_duration = 1.0 #default value  
gust_direction = Vec3(1, 0, 0)
wind_gust_velocity = Vec3(0, 0, 0)

def environmentals():
    global is_gusting, cooldown_timer, active_timer, gust_peak_speed, gust_direction, wind_gust_velocity, gust_duration
    
    #The formula for gust is in the notes 
    if not is_gusting: #Calm phase: count down to the next gust 
        cooldown_timer -= time.dt
        wind_gust_velocity = Vec3(0, 0, 0)
        
        if cooldown_timer <= 0:
            is_gusting = True 
            active_timer = 0.0 
            gust_peak_speed = random.uniform(3.0, 8.0) #gust speed
            gust_duration = random.uniform(1.0, 10.0) #gust duration

            angle = random.uniform(0, 2 * math.pi) #unit vector direction
            gust_direction = Vec3(Vec3(math.cos(angle), 0, math.sin(angle)).normalized())

    else: #Active phase: runs 1 - cosine curve 
        active_timer += time.dt

        if active_timer >= gust_duration: #Gust finished, reseting variables
            is_gusting = False
            cooldown_timer = random.uniform(3.0, 10.0)
            wind_gust_velocity = Vec3(0, 0, 0)
        else: #calculating velocity 
            progress = active_timer / gust_duration
            V_curent = (gust_peak_speed/2.0) * (1 - math.cos(2.0 * math.pi * progress))
            wind_gust_velocity = gust_direction * V_curent
        print(wind_gust_velocity)
    #Turbulance

#Motor manager - ESC(Electronic Speed Controller)
def ESC(T, torque_applied_x, torque_applied_y, torque_applied_z):
    global motor_speed_array, Ang_v_RAD
    #Using the formula mentioned in notes to calculate each motors force
    Cq = k_torque / k_thrust
    force_motor_1 = T/4 + (torque_applied_x/(4*d)) - (torque_applied_z/(4*d)) + (torque_applied_y/(4*Cq))
    force_motor_2 = T/4 - (torque_applied_x/(4*d)) - (torque_applied_z/(4*d)) - (torque_applied_y/(4*Cq))
    force_motor_3 = T/4 + (torque_applied_x/(4*d)) + (torque_applied_z/(4*d)) - (torque_applied_y/(4*Cq))
    force_motor_4 = T/4 - (torque_applied_x/(4*d)) + (torque_applied_z/(4*d)) + (torque_applied_y/(4*Cq))
        
    force_motor_1 = clamp(force_motor_1, 0, 20)
    force_motor_2 = clamp(force_motor_2, 0, 20)
    force_motor_3 = clamp(force_motor_3, 0, 20)
    force_motor_4 = clamp(force_motor_4, 0, 20)

    #Converts force in newtons to angular velocity in rad/s
    angular_v_motor_1 = math.sqrt(force_motor_1/k_thrust)
    angular_v_motor_2 = math.sqrt(force_motor_2/k_thrust)
    angular_v_motor_3 = math.sqrt(force_motor_3/k_thrust)
    angular_v_motor_4 = math.sqrt(force_motor_4/k_thrust)

    #Calculate the lag in each angular velocity and add the speed to the speed arrray
    motor_speed_array[0] += ((angular_v_motor_1 - motor_speed_array[0]) / motor_responsetime) * time.dt
    motor_speed_array[1] += ((angular_v_motor_2 - motor_speed_array[1]) / motor_responsetime) * time.dt
    motor_speed_array[2] += ((angular_v_motor_3 - motor_speed_array[2]) / motor_responsetime) * time.dt
    motor_speed_array[3] += ((angular_v_motor_4 - motor_speed_array[3]) / motor_responsetime) * time.dt

    #Converting speeds into motion again but this time with the new speed values
    F1 = k_thrust * (motor_speed_array[0]) ** 2
    F2 = k_thrust * (motor_speed_array[1]) ** 2
    F3 = k_thrust * (motor_speed_array[2]) ** 2
    F4 = k_thrust * (motor_speed_array[3]) ** 2
    f_total = F1 + F2 + F3 + F4 
    torque_x = d * (F1 + F3 - F2 - F4) #real motors(m1, m3) push the tail up
    torque_z = d * (F3 + F4 - F1 - F2) #left motors(m3, m4) roll the drone right
    torque_y = k_torque * ((motor_speed_array[0]**2) + (motor_speed_array[3]**2) - (motor_speed_array[1]**2) - (motor_speed_array[2]**2))

    return f_total, torque_x, torque_y, torque_z

plane = Entity(model='plane', scale=(30, 1, 30), color=color.green)

camera.position = (0, 5, -20)
camera.rotation_x = 10

drone = Entity(model='cube', color=color.orange)
drone.mass = m 
drone.position_y = 0.5 

hud = Text(text="", position=(-0.85, 0.45))

def update():
    #To follow the drone
    camera.position = drone.position + Vec3(0, 5, -15)
    camera.look_at(drone)

    global T, v, Ang_v_RAD, torque_applied, target_yaw_rad, motor_speed_array #Global variables are required to be declared inside the func
    #Here will be the physics implementation

    #This is the reset key 
    if held_keys['r']:  
        drone.position = Vec3(0, 0.5, 0)
        drone.rotation = Vec3(0, 0, 0)
        v = Vec3(0, 0, 0)
        Ang_v_RAD = Vec3(0, 0, 0)
        T = 0.0
        motor_speed_array = [0.0, 0.0, 0.0, 0.0]

    thrust_rate = 10
    torque_strength = 0.5 

    #Thrust control 
    T += held_keys["space"] * time.dt * thrust_rate
    T -= held_keys["shift"] * time.dt * thrust_rate
    T = clamp(T, 0, 20)

    #Yaw stabalization
    current_angle_yaw = math.radians(angleRange(drone.rotation_y))
    yaw_input = held_keys['a'] - held_keys['d']

    if yaw_input != 0:
        torque_applied.y = yaw_input * torque_strength
        target_yaw_rad = current_angle_yaw
    else: 
        #This will calculate shortest distance between target and current and then put it in the torque.y 
        angle_diff = target_yaw_rad - current_angle_yaw
        yaw_error = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
        torque_applied.y = (yaw_error * P_yaw) - (Ang_v_RAD.y * D_yaw)

    #stabalization
    current_angle_pitch = math.radians(angleRange(drone.rotation_x))
    current_angle_roll = math.radians(angleRange(drone.rotation_z))

    target_angle_pitch = (held_keys['w'] - held_keys['s']) * max_tilt  # X-axis (Pitch)
    target_angle_roll =  (held_keys['e'] - held_keys['q']) * max_tilt  # Z-axis (roll)

    error_pitch = target_angle_pitch - current_angle_pitch
    error_roll = target_angle_roll - current_angle_roll

    torque_applied.x = (error_pitch * P) - (Ang_v_RAD.x * D)
    torque_applied.z = (error_roll * P) - (Ang_v_RAD.z * D)

    actual_f_total, torque_applied.x, torque_applied.y, torque_applied.z = ESC(T, torque_applied.x, torque_applied.y, torque_applied.z)

    torque_drag = -Ang_v_RAD * k_drag #Ang_v_RAD is the max angular rotation. It means the top rotation speed will be about 170 deg / s 

    torque_net = torque_applied + torque_drag

    ang_acceleration = Vec3(torque_net.x / I.x, torque_net.y / I.y, torque_net.z / I.z) #f=ma for rotational

    Ang_v_RAD = Ang_v_RAD + (ang_acceleration * time.dt)

    Ang_v_DEG = Ang_v_RAD * RAD_TO_DEG #the unit is deg/s for each axis

    drone.rotation_x += Ang_v_DEG.x * time.dt   # Pitch
    drone.rotation_y += Ang_v_DEG.y * time.dt  # Yaw
    drone.rotation_z += Ang_v_DEG.z * time.dt  # Roll


    environmentals()

    #Forces calculation
    f_gravity = Vec3(0, -drone.mass * 9.81, 0)
    f_thrust = drone.up * actual_f_total #thrust and drag apply in all directions that's why
    f_drag = -v * k         #they will be added universally while gravity is only for down
    f_net = f_thrust + f_gravity + f_drag

    #We will use acceleration to get velocity 
    acceleration = f_net/ drone.mass #f = ma
    v += acceleration * time.dt #Eular Numerical part    
    drone.position += v * time.dt #Eular Numerical part 

    #if it collides with the ground
    if drone.y < 0.5:
        drone.y = 0.5
        if v.y < 0: #check for if vertical component is pointing downwards
            v.y = 0 
        v.x *= 0.9 #slowly resetting velocity of other axis as well
        v.z *= 0.9 
        Ang_v_RAD *= 0.1 #This reduces the angular velocity by 10% every frame it is touching the ground

    hud.text = f"""
    Thrust: {T:.1f} N
    Linear Vel: ({v.x:.1f}, {v.y:.1f}, {v.z:.1f}) m/s
    Angular Vel: ({Ang_v_DEG.x:.0f}, {Ang_v_DEG.y:.0f}, {Ang_v_DEG.z:.0f}) deg/s
    Position: ({drone.world_x:.0f}, {drone.world_y:.0f}, {drone.world_z:.0f})
    Orientation: ({drone.rotation_x:.0f}, {drone.rotation_y:.0f}, {drone.rotation_z:.0f}) deg
    """

app.run()  


