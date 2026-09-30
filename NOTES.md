## Notes
I have brainstormed the idea with Gemini, and it has given me a rough plan on how to approach this project. 

I will use Ursina Engine built on Panda3D to create the 3D environment

I am staring the work by reading the Ursina documentation and noting down things important for me. 

## Ursina
This library will be used to generate the the 3D stuff. 

# Getting started code breakdown

It has entities which is a thing u place 
first parameter (model) is what it is like a cube sphere quad
Next parameter is the color of the model

Positive x is right, positive y is up, and positive z is forward

the update func is called every frame by the engine 

the held_keys is a dict which stores all the keys and 0 if key not pressed and 1 if it is pressed. 

time.dt is time since last frame. * by this makes the player move at the same speed even if the game has a different speed. We do this so instead of moving per frame which can be different, the player moves per second. 

the input(key) func is activated everytime a key is pressed or mouse buttone etc. U can then check if the key is a key like eg space

Invoke is used to trigger actions after a delay. it's parameters are like these eg: invoke(setattr, player, 'y', player.y-1, delay=.25)

Difference between update and input function: Update is for continous keys while input is for key presses, so basically if I wanna hold smthg down put it in update and if I wanna press it once put it in input

app.run() is used to actually run the game



# Entities and their attributes
Every entity has a parent child relationship with another object. New entites are kids of the scene but we can change them by going  parent=camera.ui in the attributes

the camera.ui is a built in parent which is used to create main menus etc where it sticks to the screen and is a 2D flat layout. 

We can declare entity as blank and then add attributes as well
eg  e = Entity()
    e.position = Vec3(0,0,0)

vec3 (3D vectors) are used to store positions and they allow for easy vector math for movement etc

there is a vec2 (2d vector) as well

collider is added by the attribute collider = 'eg box'

- model (input custom ones as well in obj format)
- texture (what it looks like. Can import images etc)
- color 
- position (in form of vec3 as well)
- rotation 
- scale
- update (automatically called as we are putting it in main.py)
- input (automatically called as we are putting it in main.py)
- mouse input (entity must have a collider for the mouse stuff. 
    mouser.hovered_entity reutns exact entity under the mouse
    my_entity.hovered tells if the mouse is resting on a specfic object
    on_click(), on_double_click(), on_mouse_enter(), on_mouse_exit())


all properties can be modified later by entity.property = and then the change.

# Coordinate system
we can rotate stuff using these commands:
- entity.rotation_directions(position)
- entity.look_at(position)
- entity.look_at_2d(position)
- entity.rotate(amount) this adds rotation to the current rotation

# Collion 
To add colliders in two ways:
-we can add them when creating the entity e = Entity(model='cube', collider='box')
-we do Collider(entity name, center=Vec3(position), size=Vec3(size))

the first way is to make collider exactly like our model and the second one is for making collider custom fitted.

hitinfo: When we use raycast, boxcast or intersection, a hitinfo object is 
generated which contains: 
-hit: false or true
-entity: that was hit
-point: coordinate where this happend
-distance: how far away was the object when it got hit

Raycast(): shoots an thin invisible laser from a point in a direction. If it hits anything, it reports what it hit. It is used to see if a wall is infront of the player before letting them move forward or gun mechanics.

hit_info = raycast(origin, direction, distance, ignore=(self,))
if hit_info.hit is false, it means the path is clear. hit_info variable can be named anything else as well.

boxcast(): shoots a thick beam (like a rectangle box). Good for when a player is moving through a doorway 

.intersects(): Checks if two solid objects are currently overlapping or touching. Good for triggering events when a player enters a zone. 

if player.intersects(trigger_box).hit:
    trigger_box(color = color.red)

distance(): tells distance

distance(player, pickup)

Mouse collision: the game constantly shoots a raycast out of my mouse pointer. it tells where the mouse is pointing in using mouse.world_point.

# 3D animations
Frame animation loads a sequence of models and cycles them so it looks animated. 

To do this FrameAnimation3d('run_cycle_')

# Camera 
Camera is our eyes and it is built in so we just need to modify it.

It is an entity so it can be changed using .property 

camera.loot_at(entity name): locks target on a entity. 

camera.fov: controls vision. low fov is like zoom

camera.clip_plane_near: closest distance (in units) an object can get to the camera before it becomes invisible/disappears.

camera.clip_plane_far: maximum distance (in units) an object can get to the camera before it leaves the camera pov.

increase/decrease to change rendering distance ig.

I need both first and third person povs. But in the early stage I need 3rd person to design the drone. 

loop for third person is: 
camera.parent = player       # The camera is now glued to the player
camera.position = (0, 3, -7) # Position relative to the player (3 up, 7 behind)
camera.rotation_x = 15       # Tilt slightly down to look at the player

This makes the camera a child of the player.

# light sources
we need to import shaders to use them. Also add shader=lit_with_shadows_shader for all entities. 

1. Ambient light: this is the default and it lights the whole world equally from all directs. No shadows or highlights. 
ambient = AmbientLight (color=color.rgb(100, 100, 100))

2. Directional Light (Sun): its like the sun. Its position does not matter only its direction does. all its ray are parrallel to each other. 
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1)) 

3. Point Light (light bulb): emits in all direction from a specific point. Closer objects are brightly lit while further away objects are faded. 
bullet_glow = PointLight(position=Vec3(0, 2, 0), color=color.red)

4. Spot Light (flashlight): Cone of light in a specific direction from a specific point. 


drone.up = this returns the vec3 vector which is pointing straight out of the local top of the drone. 

same for down, forward, back, left, right.s

clamp is used for ranges. 