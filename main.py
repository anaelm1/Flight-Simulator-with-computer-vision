from ursina import *

app = Ursina()


"""player = Entity(model = 'sphere', color = color.blue, scale_y=2)

def update():
    player.y += held_keys['w'] * time.dt 
    player.y -= held_keys['s'] * time.dt 

def input(key):
    if key == "space":
        player.y += 1
        invoke(setattr, player, 'y', player.y-1, delay=.25)"""

def action():
    print('Ow! That hurt!')

Entity(model='quad', parent=camera.ui, scale=.1, collider='box', on_click=action) # on_click should be a function/callable/Func/Sequence


app.run()