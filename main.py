#Main code is here for now

'''
v = 3rd person window toggle
r = reset the drone
h = auto hover
'''

import math 
import random 
import numpy as np
import csv
import datetime

from ursina import *
app = Ursina()

#keeps the angles between -180 and 180
def angleRange(angle):
    return (angle + 180) % 360 - 180 

#Global Variables:
m = 1.5 #kg
g = 9.81 #m/s^2
v = Vec3(0, 0, 0)
Ang_v_RAD = Vec3(0, 0, 0) # rad/s . angular velocity 
air_density_base = 1.225 #kg/m3
air_density = 1.225 #this is the dynamic air density but I am giving this the same default value but it will be calculated soon
cross_sectional_area = 0.2 #1 is the cross sectional area by formula but the drone is mostly an open body 

k_drag = 0.05 #drag coefficient. Random Value for now
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
max_tilt = math.radians(30.0) #max the drone can tilt to a side
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

#anti crash mechanism status
anti_crash = False 
has_taken_off = False
flight_timer = 0.0

#Auto Hover
auto_hover = False
auto_hover_altitude = 0

#wind fighter
wind_fighter = False
anchor_position = Vec3(0, 0, 0)

#CSV flight logging
log_filename = f"flight_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
csv_file = open(log_filename, mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Time', 'PositionX', 'PositionY', 'PositionZ', 'VelocityX', 'VelocityY', 'VelocityZ', 'Thrust', 'AutoHover', 'WindFighter', 'AntiCrash'])
log_timer = 0.0


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
    dt = max(time.dt, 0.001)

    #Prevents division by 0 
    V = max(v_relative_mag, 0.5) #V is velocity 
    h = max(altitude, 0.5) #h is height

    #setting up Spatial length scales
    L_w = h # y axis (vertical) scales directly with the height above the ground
    denominator_scale = max(0.1, (0.177 + 0.000823 * h) ** 1.2)
    L_u = h / denominator_scale #x axis (horizontal) expand near the surface so this is the formula
    L_v = h / denominator_scale #z axis (horizontal) expand near the surface so this is the formula

    #calculating time constants 
    timeConstant_u = L_u / V
    timeConstant_v = L_v / V
    timeConstant_w = L_w / V 

    #prevents division by 0
    timeConstant_u = max(timeConstant_u, 0.05)
    timeConstant_v = max(timeConstant_v, 0.05)
    timeConstant_w = max(timeConstant_w, 0.05)

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
            gust_peak_speed = random.uniform(2.0, 7.0) #gust speed
            gust_duration = random.uniform(4.0, 7.0) #gust duration

            angle = random.uniform(0, 2 * math.pi) #unit vector direction
            gust_direction = Vec3(Vec3(math.cos(angle), 0, math.sin(angle)).normalized())

    else: #Active phase: runs 1 - cosine curve 
        active_timer += time.dt
        #print("gust on")
        if active_timer >= gust_duration: #Gust finished, reseting variables
            is_gusting = False
            cooldown_timer = random.uniform(7.0, 12.0)
            wind_gust_velocity = Vec3(0, 0, 0)
        else: #calculating velocity 
            progress = active_timer / gust_duration
            V_curent = (gust_peak_speed/2.0) * (1 - math.cos(2.0 * math.pi * progress))
            wind_gust_velocity = gust_direction * V_curent

    #Turbulance: 

    v_relative = v - wind_total_velocity     #relative velocity vector
    airspeed = v_relative.length()
    altitude = drone.y
    severity = 1.5 #moderate turbulence 

    wind_turbulence_velocity = dryden_model(airspeed, altitude, severity)

    #air density scaling (formula in notes)
    air_density = air_density_base * max(0.2, 1.0 - (drone.y * 0.0001))

#Motor manager - ESC(Electronic Speed Controller)
def ESC(T, torque_applied_x, torque_applied_y, torque_applied_z):
    global motor_speed_array, Ang_v_RAD, air_density, anti_crash
    global flight_timer

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

    idle_force = 0.15 #This is for realistic free fall

    #Anti Crash Mechanism: This will apply thrust if the drone is descending at a high rate/stalling
    #I am adding a hysteresis(dead zone) which will stop the flicking of true false    
    if not anti_crash:
        if v.y < -3.0 and has_taken_off and drone.y < 12.0 and drone.y > 0.8 and flight_timer > 1.5 and not held_keys["shift"]:
            anti_crash = True
    else:
        if v.y >= -0.3 or drone.y <= 0.75 or drone.y >= 15.0 or held_keys["shift"]: 
            anti_crash = False

    if anti_crash: #Pushing motors to maximum physical limit in a do or die situation
        F1 = 30
        F2 = 30
        F3 = 30
        F4 = 30

    if anti_crash:
        max_limit = 32
    else:
        max_limit = 20

    #Adding Motor desaturation (makes sure no motor exceeds max limit of 0.15 to 20 N )
    F1 = clamp(F1, idle_force, max_limit)
    F2 = clamp(F2, idle_force, max_limit)
    F3 = clamp(F3, idle_force, max_limit)
    F4 = clamp(F4, idle_force, max_limit)
        
    f_total = F1 + F2 + F3 + F4 

    forces = [F1, F2, F3, F4]

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

screen_aspect = window.aspect_ratio

#Third person camera 
third_cam_active = True
second_cam_entity = Entity() #Making the camera 
second_cam = base.cam.node().make_copy() #copying the lens and stuff of the main camera
second_cam_np = second_cam_entity.attach_new_node(second_cam) #The window itself

#Panel dimensions math and stuff.
PANEL_LEFT   = 0.73
PANEL_RIGHT  = 0.97
PANEL_BOTTOM = 0.68
PANEL_TOP    = 0.93

second_cam_panel = base.win.make_display_region(PANEL_LEFT, PANEL_RIGHT, PANEL_BOTTOM, PANEL_TOP)
second_cam_panel.set_sort(10)
second_cam_panel.set_camera(second_cam_np)

ui_width = (PANEL_RIGHT - PANEL_LEFT) * screen_aspect
ui_height = PANEL_TOP - PANEL_BOTTOM
ui_x = ((PANEL_LEFT + PANEL_RIGHT) / 2 - 0.5) * screen_aspect
ui_y = (PANEL_TOP + PANEL_BOTTOM) / 2 - 0.5

panel_frame = Entity(parent=camera.ui, model='quad', color=color.black66, scale=(ui_width + 0.02, ui_height + 0.02), x=ui_x, y=ui_y, z=-1, unlit=True, texture='white_cube')
panel_text = Text(text="3RD PERSON VIEW", parent=camera.ui, scale=1.1, color=color.black, x=ui_x, y=ui_y - (ui_height / 2) - 0.03, origin=(0,0))

#Crosses as a navigation goal 
waypoints = [
    Vec3(random.uniform(-200, 200), random.uniform(2, 20), random.uniform(-200, 200),),
    Vec3(random.uniform(-200, 200), random.uniform(2, 20), random.uniform(-200, 200),),
    Vec3(random.uniform(-200, 200), random.uniform(2, 20), random.uniform(-200, 200),),
    Vec3(random.uniform(-200, 200), random.uniform(2, 20), random.uniform(-200, 200),)
    ]

current_waypoint_index = 0

cross1 = Entity(position=waypoints[current_waypoint_index])
horizontal_bar = Entity(parent=cross1, model='cube', scale=(10, 0.2, 1), color=color.red) 
vertical_bar = Entity(parent=cross1, model='cube', scale=(1, 0.2, 7), color=color.red)

'''
#trees
for i in range(50):
    tree_x = random.uniform(-60, 60)
    tree_z = random.uniform(-60, 60)
    tree_height = random.uniform(10, 40)
    if math.hypot(tree_x, tree_z) > 8: #if they are closer then 8 to the spawn then they won't be produced
        tree = Entity(name='tree', model='cube', color=color.brown, scale=(5, tree_height, 5), position=(tree_x, 2.5, tree_z), collider='box')
'''

#hud panel with physical values
hud_box_width = 0.50
hud_box_height = 0.20

hud_panel = Entity(model='quad', parent=camera.ui, position=(-0.35 * screen_aspect, 0.30), color=color.black66, scale=(hud_box_width, hud_box_height), unlit=True, texture='white_cube', z=0)
hud = Text(parent=camera.ui, text="", position=(-0.50 * screen_aspect, 0.41), color=color.white, scale=1.0, z=-1)

#Audios
rotor_audio = Audio('drone_rotor_audio.wav', loop=True, autoplay=True, volume=0.0)
wind_audio = Audio('wind_audio.wav', loop=True, autoplay=True, volume=0.0)
anti_crash_audio = Audio('anti_crash_audio.wav', loop=True, autoplay=True, volume=0.0)

def input(key):
    global third_cam_active, auto_hover, auto_hover_altitude, wind_fighter
    if key == 'v':
        third_cam_active = not third_cam_active
        second_cam_panel.setActive(third_cam_active)
        panel_frame.enabled = third_cam_active
        panel_text.enabled = third_cam_active
    if key == 'h':
        auto_hover = not auto_hover
        if auto_hover:
            auto_hover_altitude = drone.y
    '''
    if key == 'f':
        wind_fighter = not wind_fighter
        if wind_fighter:
            anchor_position = Vec3(drone.x, drone.y, drone.z)
            #print(f"Wind Fighter Enabled. Holding Position at: {anchor_position}")
    '''
            
def update():
    #Here will be the main implementation: Physics and Game mechanics both
    global T, v, Ang_v_RAD, torque_applied, target_yaw_rad, motor_speed_array, last_capture_time, anti_crash, has_taken_off #Global variables are required to be declared inside the func
    global auto_hover, auto_hover_altitude, flight_timer, wind_fighter, anchor_position
    global current_waypoint_index
    global log_timer, csv_writer, csv_file

    #Making pip size change with the aspect ratio
    screen_aspect = window.aspect_ratio
    ui_width = (PANEL_RIGHT - PANEL_LEFT) * screen_aspect
    ui_height = PANEL_TOP - PANEL_BOTTOM
    ui_x = ((PANEL_LEFT + PANEL_RIGHT) / 2 - 0.5) * screen_aspect
    ui_y = (PANEL_TOP + PANEL_BOTTOM) / 2 - 0.5

    panel_frame.scale = (ui_width + 0.02, ui_height + 0.02)
    panel_frame.position = Vec3(ui_x, ui_y, -1)
    panel_text.position = Vec3(ui_x, ui_y - (ui_height / 2) - 0.03, 0)

    #To follow the drone
    if third_cam_active:
        second_cam_entity.position = drone.position + Vec3(0, 3, -8)
        second_cam_entity.look_at(drone)

    thrust_rate = 15
    torque_strength = 0.5 

    #Auto Hold
    if auto_hover:
        if held_keys["space"] or held_keys["shift"]: #deactiving it if the player is taking control again 
            auto_hover = False
        else:
            base_thrust = drone.mass * 9.81 #base counterforce
            altitude_error = auto_hover_altitude - drone.y
            correction = (altitude_error * P) - (v.y * D) #formula in notes
            T = base_thrust + correction
            T = clamp(T, 0, 35)

    #Thrust control 
    T += held_keys["space"] * time.dt * thrust_rate
    T -= held_keys["shift"] * time.dt * thrust_rate
    T = clamp(T, 0, 35)

    #Yaw stabalization
    current_angle_yaw = math.radians(angleRange(drone.rotation_y))
    yaw_input =  held_keys['d'] - held_keys['a']

    if yaw_input != 0:
        torque_applied.y = yaw_input * torque_strength
        target_yaw_rad = current_angle_yaw
    else: 
        #This will calculate shortest distance between target and current and then put it in the torque.y 
        angle_diff = target_yaw_rad - current_angle_yaw
        yaw_error = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
        torque_applied.y = (yaw_error * P_yaw) - (Ang_v_RAD.y * D_yaw)

    #stabilization
    current_angle_pitch = math.radians(angleRange(drone.rotation_x))
    current_angle_roll = math.radians(angleRange(drone.rotation_z))

    target_angle_pitch = (held_keys['w'] - held_keys['s']) * max_tilt  # X-axis (Pitch)
    target_angle_roll =  (held_keys['e'] - held_keys['q']) * max_tilt  # Z-axis (roll)

    '''
    #Wind fighter
    if wind_fighter:
        if held_keys['w'] or held_keys['s'] or held_keys['e'] or held_keys['q']:
            anchor_position = Vec3(drone.x, drone.y, drone.z)
        else:
            # World-space distance error from our locked anchor point
            error_x = drone.x - anchor_position.x
            error_z = drone.z - anchor_position.z

            #  Rotate world-space errors into the drone's body frame (Local X = Forward, Local Z = Right)
            yaw_rad = math.radians(angleRange(drone.rotation_y))
            cos_y = math.cos(yaw_rad)
            sin_y = math.sin(yaw_rad)

            local_error_x =  error_x * cos_y + error_z * sin_y
            local_error_z = -error_x * sin_y + error_z * cos_y

            # Rotate world velocity into local body frame for damping
            local_vx = v.x * cos_y + v.z * sin_y
            local_vz = -v.x * sin_y + v.z * cos_y

            # PD Controller: Proportional gain pulls to position, Derivative gain kills momentum/oscillation
            kp = 0.12  # Position correction gain
            kd = 0.08  # Velocity damping gain

            # To fix a positive position error (drifted forward), we need a negative pitch (pitch forward into wind)
            correction_pitch = clamp(-(local_error_x * kp + local_vx * kd), -max_tilt, max_tilt)
            # To fix a positive lateral error (drifted right), we need a positive roll (roll left)
            correction_roll  = clamp( (local_error_z * kp + local_vz * kd), -max_tilt, max_tilt)

            target_angle_pitch += correction_pitch
            target_angle_roll  += correction_roll
    '''

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
    
    '''
    #checking any crashes with obstacles(trees)
    prev_position = drone.position
    next_position = drone.position + (v * time.dt)
    
    crashed = False

    for entity in scene.entities:
        if entity.name == "tree":
            horizontal_distance = math.hypot(next_position.x - entity.x, next_position.z - entity.z)
            if horizontal_distance < (entity.scale.x * 1.2) and (0 <= next_position.y <= 7.0):
                break

    if crashed:
        #If we crash, these things will happen: Kill velocity, bounce backward, drop thrust, sound alarm
        drone.position = prev_position        
        v = -v * 0.4 #bounce back
        T = max(0.0, T - 10.0) #Drop in power
        Ang_v_RAD *= 0.2 #spin slightly
        anti_crash_audio.volume = 0.5 #Warning audio
    else: 
        drone.position = next_position
    '''

    #if it collides with the ground
    if drone.y <= 0.5:
        drone.y = 0.5
        if v.y < 0: #check for if vertical component is pointing downwards
            v.y = 0 
        v.x *= 0.9 #slowly resetting velocity of other axis as well
        v.z *= 0.9 
        Ang_v_RAD *= 0.1 #This reduces the angular velocity by 10% every frame it is touching the ground

    if drone.y > 1.0:
        has_taken_off = True
        flight_timer += time.dt

        
    #Cross navigation system and hud text
    display_altitude = drone.y - 0.5

    if distance(drone, cross1) <= 2.5:
        current_waypoint_index = (current_waypoint_index + 1) % len(waypoints)        
        cross1.position = waypoints[current_waypoint_index]

    distance_to_target = distance(drone, cross1)
    hud.text = f"""
        THRUST: {T:5.1f} N
        ALTITUDE: {display_altitude:5.1f} m
        SPEED: {v.length():5.1f} m/s
        VELOCITY: ({v.x:4.1f}, {v.y:4.1f}, {v.z:4.1f}) m/s
        AUTO HOVER: <green>{auto_hover}<default>
        {"<red>ANTI CRASH ENGAGED!<default>" if anti_crash else "ANTI CRASH: <green>False<default>"}
        <cyan>WAYPOINT [{current_waypoint_index + 1}/{len(waypoints)}] DIST: {distance_to_target:.1f}m<default>
        """
        
    update_audio()

    #This is the reset key
    if held_keys['r']:  
        drone.position = Vec3(0, 0.5, 0)
        drone.rotation = Vec3(0, 0, 0)
        v = Vec3(0, 0, 0)
        Ang_v_RAD = Vec3(0, 0, 0)
        T = 0.0
        motor_speed_array = [0.0, 0.0, 0.0, 0.0]
        torque_applied = Vec3(0, 0, 0)
        target_yaw_rad = 0.0
        actual_f_total = 0

    #CSV flight data logging
    log_timer += time.dt
    if log_timer >= 1.0: #i am logging data every 1 second
        log_timer = 0.0
        csv_writer.writerow([
            round(flight_timer, 2),
            round(drone.x, 2), round(drone.y, 2), round(drone.z, 2),
            round(v.x, 2), round(v.y, 2), round(v.z, 2),
            round(T, 2), int(auto_hover), int(anti_crash)
        ])

#loop to manage rotor, wind, anti crash audios
def update_audio():
    #Dynamic rotor audio
    avg_rpm = sum(motor_speed_array) / 4.0
    speed_ratio = clamp(avg_rpm / 50.0, 0.0, 1.0) #getting a ratio of the rpm
    rotor_audio.volume = speed_ratio * 30.0 #max volume is 30

    #Dynamic wind speed 
    windspeed = wind_total_velocity.length()
    wind_speed_ratio = clamp(windspeed / 35.0, 0.0, 1.0)
    wind_audio.volume = clamp(wind_speed_ratio * 1.2, 0.0, 1.0)
    wind_audio.pitch = 0.8 + (wind_speed_ratio * 0.4)

    #Anti crash audio
    if anti_crash:
        anti_crash_audio.volume = 0.5
    else:
        anti_crash_audio.volume = 0.0

app.run()  


