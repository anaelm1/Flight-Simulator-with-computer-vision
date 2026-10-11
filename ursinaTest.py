from ursina import *
from ursina.shaders import lit_with_shadows_shader
app = Ursina()


plane = Entity(shader=lit_with_shadows_shader, name='plane', model = 'plane', collider='box', color=color.blue, scale=(20, 1, 5), position=Vec3(0,0,0))
player = Entity(shader=lit_with_shadows_shader, position=(0,0.3,0), name='Player', model='sphere', collider='sphere', color=color.red)
box = Entity(shader=lit_with_shadows_shader, position=Vec3(5,0.3,0), name = 'box', model='cube', collider='box', color=color.green)

spot = SpotLight(Postition=Vec3(5,0.3,0), color=color.yellow)

spot.look_at(box.position + Vec3(1,1,0))

camera.position = (0, 5, -10)


def update():
    player.x -= held_keys['a'] * time.dt 
    player.x += held_keys['d'] * time.dt 
    player.y += held_keys['w'] * time.dt 
    player.y -= held_keys['s'] * time.dt 
    player.z -= held_keys['q'] * time.dt 
    player.z += held_keys['e'] * time.dt 
    camera.look_at(player)



    if player.intersects(box):
        plane.color = color.pink
    else:
        plane.color = color.blue


app.run()