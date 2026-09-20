## Notes
I have brainstormed the idea with Gemini, and it has given me a rough plan on how to approach this project. 

I will use Ursina Engine built on Panda3D to create the 3D environment

I am staring the work by reading the Ursina documentation and noting down things important for me. 

## Ursina
This library will be used to generate the the 3D stuff. 

#Getting started code breakdown

It has entities which is a thing u place 
first parameter is what it is basic like cube sphere quad
Next parameter is the color of the model

Positive x is right, positive y is up, and positive z is forward

the update func is called every frame by the engine 

the held_keys is a dict which stores all the keys and 0 if key not pressed and 1 if it is pressed. 

time.dt is time since last frame. * by this makes the player move at the same speed even if the game has a different speed.  

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

collider is added by the attribute collider = 'eg box'

- model (input custom ones as well in obj format)
- texture (wait)
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
