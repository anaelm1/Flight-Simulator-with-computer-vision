#Main code is here for now

import math 
import random 

from ursina import *
app = Ursina()

#keeps the angles between -180 and 180
def angleRange(angle):
    return (angle + 180) % 360 - 180 

#Global Variables:
m = 1 #kg
g = 9.81 #m/s^2
v = Vec3(0, 0, 0)
Ang_v_RAD = Vec3(0, 0, 0) # rad/s . angular velocity 
air_density_base = 1.225 #kg/m3
air_density = 1.225 #this is the dynamic air density but I am giving this the same default value but it will be calculated soon
cross_sectional_area = 0.2 #1 is the cross sectional area by formula but the drone is mostly an open body 

k_drag = 0.4 #drag coefficient. Random Value for now
T = 0.0 #Thrust level
L = 0.1 #m .Arms length.
d = L/math.sqrt(2) #prependicular arm distance to the x and z axis
k_thrust = 1 #thrust coefficient. Random value for now 
k_torque = 0.2 #torque coefficent. Random value for now 
k_motordrag = 0.1 #Motor drag coefficent. Random value for now 
motor_responsetime = 0.02 #motor lag . Random value rightnow
motor_speed_array = [0.0, 0.0, 0.0, 0.0] #rad/s for each motor. m1, m2, m3, m4

torque = Vec3(0, 0, 0)
k_drag_rotational = 0.3 #rotatinal drag coeefficent.
I_x = 0.167 #Moment of intertia x
I_y = 0.167 #Moment of intertia y
I_z = 0.167 #Moment of intertia z
I = Vec3(I_x, I_y, I_z) #Moment of intertia
torque_applied = Vec3(0, 0, 0)

RAD_TO_DEG = 180.0 / math.pi

P = 6.0 #constant with which we pull towards target angle
D = 2.5 #damping coefficient 
P_yaw = 6.0
D_yaw = 1.0 
max_tilt = math.radians(20.0) #max the drone can tilt to a side
target_yaw_rad = 0.0 #this is the default position of a drone 


#Environmentals
wind_steady_velocity = Vec3(1.5, 0, 0) #1.5 m/s horizontal wind blowing from west to east across the map

is_gusting = False
cooldown_timer = 5.0 #seconds before first gust 
active_timer = 0.0 
gust_peak_speed = 0.0
gust_duration = 1.0 #default value  
gust_direction = Vec3(1, 0, 0)
wind_gust_velocity = Vec3(0, 0, 0)

#u is x axis, v is y axis, w is z axis

wind_turbulence_velocity = Vec3(0, 0, 0)
u_g = 0.0 #1st order state for u (front back)
v_g1 = 0.0 #2nd order state for v (left right)
v_g2 = 0.0 #2nd order state for v (left right)
w_g1 = 0.0 #2nd order states for w (up down)
w_g2 = 0.0 #2nd order states for w (up down)

wind_total_velocity = Vec3(0, 0, 0)

#This will return 3D turbulence wind vector (u_g, v_g, w_g)
def dryden_model(v_relative_mag, altitude, severity):
    global u_g, v_g1, v_g2, w_g1, w_g2
    '''
    v_relative_mag = scalar speed of the drone relative to air mass
    altitude = drone height above ground in meters
    severity = turbulence intensity scale (0.5 = light, 1.5 = moderate, 3.0 severe)
    '''
    
    dt = time.dt 

    #Prevents division by 0 
    V = max(v_relative_mag, 0.1) #V is velocity 
    h = max(altitude, 1.0) #h is height

    #setting up Spatial length scales
    L_w = h # y axis (vertical) scales directly with the height above the ground
    L_u = h / (0.177 + 0.000823 * h) ** 1.2 #x axis (horizontal) expand near the surface so this is the formula
    L_v = h / (0.177 + 0.000823 * h) ** 1.2 #z axis (horizontal) expand near the surface so this is the formula

    #calculating time constants 
    timeConstant_u = L_u / V
    timeConstant_v = L_v / V
    timeConstant_w = L_w / V 

    #Turbulence intensities
    sigma_w = 0.1 * severity * V
    sigma_u = sigma_w / (0.177 + 0.000823 * h) ** 0.4
    sigma_v = sigma_u

    #Gaussian Random Variables
    random_variable_u = random.gauss(0.0, 1.0)
    random_variable_v = random.gauss(0.0, 1.0)
    random_variable_w = random.gauss(0.0, 1.0)

    #1st order filter for u (x axis) (formulas in notes)
    alpha_u = math.exp(-dt / timeConstant_u)
    beta_u = sigma_u * math.sqrt(max(0.0, 1.0 - alpha_u**2))

    u_g = (alpha_u * u_g) + (beta_u * random_variable_u)

    #2nd order filter for v (y axis)
    alpha_v = math.exp(-dt / timeConstant_v)
    beta_v = sigma_v * math.sqrt(max(0.0, 1.0 - alpha_v**2))

    v_g1 = (alpha_v * v_g1) + (beta_v * random_variable_v)
    v_g2 = (alpha_v * v_g2) + (dt / timeConstant_v) * v_g1

    v_g = v_g1 + math.sqrt(3.0) * (v_g1 - v_g2)

    #2nd order filter for for w (z axis)
    alpha_w = math.exp(-dt / timeConstant_w)
    beta_w = sigma_w * math.sqrt(max(0.0, 1.0 - alpha_w**2))

    w_g1 = (alpha_w * w_g1) + (beta_w * random_variable_w)
    w_g2 = (alpha_w * w_g2) + (dt / timeConstant_w) * w_g1

    w_g = w_g1 + math.sqrt(3.0) * (w_g1 - w_g2)

    wind_turbulence_velocity = Vec3(u_g, v_g, w_g)

    return wind_turbulence_velocity

def environmentals():
    
    #Gust: 1 - cos wave

    global is_gusting, cooldown_timer, active_timer, gust_peak_speed, gust_direction, wind_gust_velocity, gust_duration
    global wind_turbulence_velocity, wind_total_velocity
    global air_density

    ground_factor = clamp(drone.y / 1.0, 0.0, 1.0) #This keep the wind velocity lower around the ground
    wind_total_velocity = (wind_steady_velocity + wind_gust_velocity + wind_turbulence_velocity) * ground_factor
    
    #The formula for gust is in the notes 
    if not is_gusting: #Calm phase: count down to the next gust 
        cooldown_timer -= time.dt
        wind_gust_velocity = Vec3(0, 0, 0)
        
        if cooldown_timer <= 0:
            is_gusting = True 
            active_timer = 0.0 
            gust_peak_speed = random.uniform(1.0, 4.0) #gust speed
            gust_duration = random.uniform(1.0, 10.0) #gust duration

            angle = random.uniform(0, 2 * math.pi) #unit vector direction
            gust_direction = Vec3(Vec3(math.cos(angle), 0, math.sin(angle)).normalized())

    else: #Active phase: runs 1 - cosine curve 
        active_timer += time.dt
        #print("gust on")
        if active_timer >= gust_duration: #Gust finished, reseting variables
            is_gusting = False
            cooldown_timer = random.uniform(8.0, 12.0)
            wind_gust_velocity = Vec3(0, 0, 0)
        else: #calculating velocity 
            progress = active_timer / gust_duration
            V_curent = (gust_peak_speed/2.0) * (1 - math.cos(2.0 * math.pi * progress))
            wind_gust_velocity = gust_direction * V_curent

    #Turbulance: 

    v_relative = v - wind_total_velocity     #relative velocity vector
    airspeed = v_relative.length()
    altitude = drone.y
    severity = 0.5 #moderate turbulence 

    wind_turbulence_velocity = dryden_model(airspeed, altitude, severity)

    #air density scaling (formula in notes)
    air_density = air_density_base * max(0.1, 1.0 - (drone.y * 0.0001))

#Motor manager - ESC(Electronic Speed Controller)
def ESC(T, torque_applied_x, torque_applied_y, torque_applied_z):
    global motor_speed_array, Ang_v_RAD, air_density

    air_density_ratio = air_density / air_density_base
    k_thrust_effective = k_thrust * air_density_ratio
    k_torque_effective = k_torque * air_density_ratio

    #Ground effect(increased thrust near the ground)
    height_above_ground = max(0.0, drone.y - 0.5)
    ground_effect_factor = 1.0
    if height_above_ground < 1.0:
        ground_effect_factor = 1.0 +(0.90 * (1.0 - height_above_ground))#the effect is upto 15% (0.15)
    k_thrust_effective *= ground_effect_factor

    #Using the formula mentioned in notes to calculate each motors force
    Cq = k_torque_effective / k_thrust_effective
    force_motor_1 = T/4 + (torque_applied_x/(4*d)) - (torque_applied_z/(4*d)) + (torque_applied_y/(4*Cq))
    force_motor_2 = T/4 - (torque_applied_x/(4*d)) - (torque_applied_z/(4*d)) - (torque_applied_y/(4*Cq))
    force_motor_3 = T/4 + (torque_applied_x/(4*d)) + (torque_applied_z/(4*d)) - (torque_applied_y/(4*Cq))
    force_motor_4 = T/4 - (torque_applied_x/(4*d)) + (torque_applied_z/(4*d)) + (torque_applied_y/(4*Cq))
        
    force_motor_1 = clamp(force_motor_1, 0, 20)
    force_motor_2 = clamp(force_motor_2, 0, 20)
    force_motor_3 = clamp(force_motor_3, 0, 20)
    force_motor_4 = clamp(force_motor_4, 0, 20)

    #Converts force in newtons to angular velocity in rad/s
    angular_v_motor_1 = math.sqrt(force_motor_1/k_thrust_effective)
    angular_v_motor_2 = math.sqrt(force_motor_2/k_thrust_effective)
    angular_v_motor_3 = math.sqrt(force_motor_3/k_thrust_effective)
    angular_v_motor_4 = math.sqrt(force_motor_4/k_thrust_effective)

    #Calculate the lag in each angular velocity and add the speed to the speed arrray
    motor_speed_array[0] += ((angular_v_motor_1 - motor_speed_array[0]) / motor_responsetime) * time.dt
    motor_speed_array[1] += ((angular_v_motor_2 - motor_speed_array[1]) / motor_responsetime) * time.dt
    motor_speed_array[2] += ((angular_v_motor_3 - motor_speed_array[2]) / motor_responsetime) * time.dt
    motor_speed_array[3] += ((angular_v_motor_4 - motor_speed_array[3]) / motor_responsetime) * time.dt
    #print(motor_speed_array)

    #Converting speeds into motion again but this time with the new speed values
    F1 = k_thrust_effective * (motor_speed_array[0]) ** 2
    F2 = k_thrust_effective * (motor_speed_array[1]) ** 2
    F3 = k_thrust_effective * (motor_speed_array[2]) ** 2
    F4 = k_thrust_effective * (motor_speed_array[3]) ** 2
    f_total = F1 + F2 + F3 + F4 

    #Adding Motor desaturation (makes sure no motor exceeds max limit of 0 to 20 N )
    forces = [F1, F2, F3, F4]
    max_f = max(forces)
    min_f = min(forces)

    F1 = clamp(F1, 0, 20)
    F2 = clamp(F2, 0, 20)
    F3 = clamp(F3, 0, 20)
    F4 = clamp(F4, 0, 20)

    torque_x = d * (F1 + F3 - F2 - F4) #real motors(m1, m3) push the tail up
    torque_z = d * (F3 + F4 - F1 - F2) #left motors(m3, m4) roll the drone right
    torque_y = k_torque_effective * ((motor_speed_array[0]**2) + (motor_speed_array[3]**2) - (motor_speed_array[1]**2) - (motor_speed_array[2]**2))

    return f_total, torque_x, torque_y, torque_z

plane = Entity(model='plane', scale= (1000, 1, 1000), texture="grass_texture", collider='box')

sky = Sky()

#Shadows 
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))  
ambient = AmbientLight(color=color.rgba(150, 150, 150, 255))
 
drone = Entity()
drone.mass = m 
drone.position = (0, 2, 0)

drone_visual = Entity(parent=drone, model="drone", color=color.white, scale=0.02, y=2)

#First Person Camera
camera.parent = drone
camera.position = (0, 0.1, 0)
camera.rotation = (0, 0, 0)
camera.fov = 110

#Third person camera (confusing code. I don't  really understand it)
second_cam_entity = Entity()
second_cam = base.cam.node().make_copy() 
second_cam_np = second_cam_entity.attach_new_node(second_cam)

PANEL_LEFT   = 0.73
PANEL_RIGHT  = 0.97
PANEL_BOTTOM = 0.68
PANEL_TOP    = 0.93

second_cam_panel = base.win.make_display_region(PANEL_LEFT, PANEL_RIGHT, PANEL_BOTTOM, PANEL_TOP)
second_cam_panel.set_sort(10)
second_cam_panel.set_camera(second_cam_np)

screen_aspect = window.aspect_ratio

ui_width = (PANEL_RIGHT - PANEL_LEFT) * screen_aspect
ui_height = PANEL_TOP - PANEL_BOTTOM
ui_x = ((PANEL_LEFT + PANEL_RIGHT) / 2 - 0.5) * screen_aspect
ui_y = (PANEL_TOP + PANEL_BOTTOM) / 2 - 0.5

panel_frame = Entity(parent=camera.ui, model='quad', color=color.clear, scale=(ui_width + 0.02, ui_height + 0.02), x=ui_x, y=ui_y, z=-1)
panel_text = Text(text="3RD PERSON VIEW", parent=camera.ui, scale=1.1, color=color.black, x=ui_x, y=ui_y - (ui_height / 2) - 0.03, origin=(0,0))


#Cross as a navigation goal 
cross1 = Entity(position=Vec3(50, 0.5, 50))
Entity(parent=cross1, model='cube', scale=(4, 0.2, 1), color=color.red) #Horizontal bar of the cross
Entity(parent=cross1, model='cube', scale=(1, 0.2, 4), color=color.red) #Vertical bar of the cross

hud = Text(text="", position=(-0.85, 0.45), color=color.dark_gray)

def update():
    #To follow the drone
    second_cam_entity.position = drone.position + Vec3(0, 3, -8)
    second_cam_entity.look_at(drone)

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

    torque_drag = -Ang_v_RAD * k_drag_rotational #Ang_v_RAD is the max angular rotation. It means the top rotation speed will be about 170 deg / s 

    torque_net = torque_applied + torque_drag

    ang_acceleration = Vec3(torque_net.x / I.x, torque_net.y / I.y, torque_net.z / I.z) #f=ma for rotational

    Ang_v_RAD = Ang_v_RAD + (ang_acceleration * time.dt)

    Ang_v_DEG = Ang_v_RAD * RAD_TO_DEG #the unit is deg/s for each axis

    drone.rotation_x += Ang_v_DEG.x * time.dt   # Pitch
    drone.rotation_y += Ang_v_DEG.y * time.dt  # Yaw
    drone.rotation_z += Ang_v_DEG.z * time.dt  # Roll

    environmentals()

    v_relative = v - wind_total_velocity
    v_relative_scalar = v_relative.length()

    #Forces calculation
    f_gravity = Vec3(0, -drone.mass * 9.81, 0)
    f_thrust = drone.up * actual_f_total #thrust and drag apply in all directions that's why
    f_drag = -0.5 * air_density * k_drag * cross_sectional_area * v_relative * v_relative_scalar 
    f_net = f_thrust + f_gravity + f_drag

    #We will use acceleration to get velocity 
    acceleration = f_net/ drone.mass #f = ma
    v += acceleration * time.dt #Eular Numerical part    
    drone.position += v * time.dt #Eular Numerical part 

    #if it collides with the ground
    if drone.y <= 0.5:
        drone.y = 0.5
        if v.y < 0: #check for if vertical component is pointing downwards
            v.y = 0 
        v.x *= 0.9 #slowly resetting velocity of other axis as well
        v.z *= 0.9 
        Ang_v_RAD *= 0.1 #This reduces the angular velocity by 10% every frame it is touching the ground

    if distance(drone, cross1) <= 2.0:
        hud.text = f"""
            Thrust: {T:.1f} N
            Linear Vel: ({v.x:.1f}, {v.y:.1f}, {v.z:.1f}) m/s
            Angular Vel: ({Ang_v_DEG.x:.0f}, {Ang_v_DEG.y:.0f}, {Ang_v_DEG.z:.0f}) deg/s
            Position: ({drone.world_x:.0f}, {drone.world_y:.0f}, {drone.world_z:.0f})
            Orientation: ({drone.rotation_x:.0f}, {drone.rotation_y:.0f}, {drone.rotation_z:.0f}) deg
            Target Reached!!!
            """
    else:
        hud.text = f"""
        Thrust: {T:.1f} N
        Linear Vel: ({v.x:.1f}, {v.y:.1f}, {v.z:.1f}) m/s
        Angular Vel: ({Ang_v_DEG.x:.0f}, {Ang_v_DEG.y:.0f}, {Ang_v_DEG.z:.0f}) deg/s
        Position: ({drone.world_x:.0f}, {drone.world_y:.0f}, {drone.world_z:.0f})
        Orientation: ({drone.rotation_x:.0f}, {drone.rotation_y:.0f}, {drone.rotation_z:.0f}) deg
        Distance to target: {distance(drone, cross1)}
        """

app.run()  


