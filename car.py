# pyright: reportUndefinedVariable=false

import random
from pgzero.actor import Actor
from pygame import Rect

from settings import *

class Car:
    def __init__(self, x, y, image = None, speed = 0):
        
        self.speed = speed
        self.is_player = False
        self.lives = 5
        self.crashes = 0
        self.invincible = False
        self.actor_angle_max = 8

        self.knockback = [0, 0]
        self.knockback_speed = 0.0
        self.knockback_active = False

        self.actor = self._create_actor(x, y, image)
        self._init_brake_light(x, y)
        self._init_boost(x, y)
        self._init_crash(x, y)

        # Contador de frame para a animação de boost e crash
        self.boost_frame_counter = 0
        self.crash_frame_counter = 0
        self.frame_delay = 2 

    #======================================================================#
    # Components    
    #======================================================================#

    def _create_actor(self, x, y, image):

        if image is None:
            image = random.choice(CAR_IMAGES)
        actor = Actor(image)
        actor.pos = (x, y)
        return actor


    def _init_brake_light(self, x, y):
        self.brake_light = Actor("brake")
        self.brake_light.pos = (x, y + 20)
        self.braking = False


    def _init_boost(self, x, y):
        self.boost_images = [f"boost-{i}" for i in range(1, 7)]
        self.boost_actor = Actor(self.boost_images[0])
        self.boost_actor.pos = (x, y - 10)
        self.boost_index = 0
        self.boost_active = False


    def _init_crash(self, x, y):
        self.crash_images = [f"crash-{i}" for i in range(1, 4)]
        self.crash_actor = Actor(self.crash_images[0])
        self.crash_actor.pos = (x, y)
        self.crash_index = 0
        self.crash_active = False
        self.crash_point = (0,0)

    #======================================================================#
    # Movement & Animations
    #======================================================================#

    def move(self):
        # Atualiza posição do carro e animações.

        self.actor.y -= self.speed
        
        self.brake_light.pos = (self.actor.x, self.actor.y + 10)
        self.boost_actor.pos = (self.actor.x, self.actor.y - 10)

        self.brake_light.angle = self.actor.angle
        self.boost_actor.angle = self.actor.angle


        if self.knockback_active:
            self.actor.x += self.knockback[0]
            self.actor.y += self.knockback[1]

            # Reduz suavemente o efeito
            self.knockback[0] *= 0.85
            self.knockback[1] *= 0.85
            self.knockback_speed *= 0.85

            # Quando o efeito for pequeno, encerra
            if abs(self.knockback[0]) < 0.1 and abs(self.knockback[1]) < 0.1:
                self.knockback_active = False


        # Atualiza todas as animações ativas
        self._update_animation(self.boost_active, self.boost_actor, self.boost_images, "boost_index", "boost_frame_counter")
        self._update_animation(self.crash_active, self.crash_actor, self.crash_images, "crash_index", "crash_frame_counter", auto_disable=True) 

    #======================================================================#
    # Events
    #======================================================================#

    def throttle(self):
        self.braking = False
        self.boost_active = True
        if self.speed <= 10.0:
            self.speed += 0.1

    def brake(self):
        self.braking = True
        self.boost_active = False
        self.speed -= 0.2

    def idle(self):
        self.braking = False
        self.boost_active = False
        self.speed -= 0.01

    def cruise(self):
        self.braking = False
        self.boost_active = False
        self.speed += 0.01

    def turn_left(self):
        self.actor.x = max(100, self.actor.x - 4)
        self.actor.angle = min(self.actor.angle + 1, self.actor_angle_max)

    def turn_right(self):
        self.actor.x = min(WIDTH - 100, self.actor.x + 4)
        self.actor.angle = max(self.actor.angle - 1, -self.actor_angle_max)

    def straighten(self):
        if self.actor.angle > 0:
            self.actor.angle -= 1
        elif self.actor.angle < 0:
            self.actor.angle += 1

    def crash(self, point, side, other_vehicle):

        if self.invincible:
            return

        self.crash_active = True
        self.crash_index = 0
        self.crash_frame_counter = 0
        self.crash_point = point
        self.crashes += 1
        self.lives -= 1

        self.crash_point = point or (int(self.actor.x), int(self.actor.y))

        # posiciona o crash_actor no momento exato da colisão
        self.crash_actor.pos = self.crash_point
        self.crash_actor.image = self.crash_images[self.crash_index]
        self.crash_actor.angle = self.actor.angle

        other_vehicle.speed = -2

        # Na colisão o player é empurrado na direção oposta
        self.knockback_active = True
        self.knockback_speed = 8.0  # velocidade do empurrão

        if side == "left":
            self.knockback = [8, 0]   # empurra para direita
        elif side == "right":
            self.knockback = [-8, 0]  # empurra para esquerda
        elif side == "top":
            self.knockback = [0, 15]   # empurra para baixo
        elif side == "bottom":
            self.knockback = [0, -8]  # empurra para cima

    #======================================================================#
    # Animations Helper
    #======================================================================#

    def _update_animation(self, active, actor, images, index_attr, counter_attr, auto_disable=False):
        # Atualiza qualquer animação de sprite de forma genérica.
        # usa o frame_counter específico da animação
        counter = getattr(self, counter_attr)
        counter += 1
        if counter < self.frame_delay:
            setattr(self, counter_attr, counter)
            return
        counter = 0
        setattr(self, counter_attr, counter)

        index = getattr(self, index_attr)
        if active:
            if index < len(images) - 1:
                index += 1
            elif auto_disable:
                index = 0
                if actor == self.crash_actor:
                    self.crash_active = False
            else:
                index = len(images) - 1
        else:
            if index > 0:
                index -= 1

        setattr(self, index_attr, index)
        actor.image = images[index]
        actor.angle = self.actor.angle

    #======================================================================#
    # Draw & Rect    
    #======================================================================#

    def draw(self):

        if self.boost_index > 0:
            self.boost_actor.draw()

        self.actor.draw()
        
        if self.braking:
            self.brake_light.draw()
    

    def rect(self):
        base_margin_x = 50
        base_margin_y = 50
        angle_factor = abs(self.actor.angle) / self.actor_angle_max
        margin_x = base_margin_x + angle_factor * 20
        margin_y = base_margin_y + angle_factor * 20

        return Rect(
            self.actor.left + margin_x,
            self.actor.top + margin_y,
            self.actor.width - 2 * margin_x,
            self.actor.height - 2 * margin_y
        )
