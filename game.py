# pyright: reportUndefinedVariable=false

import random

from settings import *
from car import Car

from pgzero.actor import Actor
from pygame import Rect

#================================================================================#
# Game state
#================================================================================#
game_state = "menu"
crash = False

random_vehicles = []
timer_spawn = 0
next_spawn_time = random.uniform(1.0, 2.0)

bg_y1 = 0
bg_y2 = -HEIGHT

carousel_index = 0
carousel_x = WIDTH // 2
carousel_y = HEIGHT // 2
carousel_spacing = 600

#================================================================================#
# Start game
#================================================================================#

def start_game(current_vehicle_index):
    global game_state, sound, player

    game_state = "playing"

    player = Car(545, 650, CAR_IMAGES[current_vehicle_index], 0)
    player.is_player = True

    return player

#================================================================================#
# Update game
#================================================================================#
def update_game(dt, keyboard):
    global game_state, bg_y1, bg_y2, timer_spawn, next_spawn_time, random_vehicles, crash
    
    if game_state != "playing":
        return False

    crashes_this_frame = 0

    #============================================================================#
    # Movimento do background

    bg_y1 += bg_speed
    bg_y2 += bg_speed
    if bg_y1 >= HEIGHT:
        bg_y1 = -HEIGHT
    if bg_y2 >= HEIGHT:
        bg_y2 = -HEIGHT

    #============================================================================#
    # Controles do player

    if keyboard.up:
        player.throttle()
    elif keyboard.down:
        player.brake()
    else:
        player.idle()

    if keyboard.left:
        player.turn_left()
    elif keyboard.right:
        player.turn_right()
    else:
        player.straighten()

    player.move()

    #============================================================================#
    # Atualização dos veiculos aleatorios
    for vehicle in random_vehicles[:]: 

        too_close, other = check_vehicle_distance(vehicle, min_distance=100)

        if too_close and other:

            if vehicle.actor.y > other.actor.y:
                vehicle.speed = other.speed
                vehicle.idle()
            else:
                other.speed = vehicle.speed
                other.idle()

        vehicle.move()

        # Colisão Detectada
        if player.rect().colliderect(vehicle.rect()):
            collision_point = get_collision_point(player.rect(), vehicle.rect())
            collision_side = get_collision_side(player.rect(), vehicle.rect())

            player.crash(collision_point, collision_side, vehicle)
            crashes_this_frame += 1

            if player.lives <= 0:
                return "game_over", crashes_this_frame

        # Remove veículos fora da tela
        if vehicle.actor.y < -300 or vehicle.actor.y > HEIGHT + 300 :
            random_vehicles.remove(vehicle)

    #============================================================================#
    # Spawn veículos aleatórios
    timer_spawn += dt
    if timer_spawn >= next_spawn_time:
        spawn_random_vehicle()
        timer_spawn = 0
        next_spawn_time = random.uniform(0.5, 2.0)

    return "playing", crashes_this_frame

#================================================================================#
# Draw game
#================================================================================#
def draw_game(screen):
    screen.blit("highway-700-900", (0, bg_y1))
    screen.blit("highway-700-900", (0, bg_y2))

    player.draw()
    # screen.draw.rect(player.rect(), (0, 255, 0))

    for vehicle in random_vehicles:
        vehicle.draw()
        # screen.draw.rect(vehicle.rect(), (255, 0, 0))
    
    if player.crash_active:
        player.crash_actor.draw()

    #============================================================================#
    # Life Icons
    life_icon_spacing = 40
    start_x = 120
    y = 20

    for i in range(player.lives):
        icon = Actor("life-wheel")
        icon.pos = (start_x + i * life_icon_spacing, y + 30)
        icon.draw()
        screen.draw.text(f"Lifes:", (20, 38), color="white", ocolor="black", owidth=1, fontsize=34)


#================================================================================#
# Spawn random vehicle
#================================================================================#

def spawn_random_vehicle():
    x = random.choice(LANES_X)

    direction = random.choice(["down", "up"])

    if direction == "up":
        y = -200
        speed = -random.uniform(2.0, 7.0)
    else:
        y = HEIGHT + 200  # ou 1000 no seu caso
        speed = random.uniform(2.0, 7.0)

    if not can_spawn_vehicle(x, y, direction):
        return 

    vehicle = Car(x, y, None, 0)
    vehicle.speed = speed
    random_vehicles.append(vehicle)


def can_spawn_vehicle(x, y, direction, safe_distance= 250):
    for other in random_vehicles:
        if abs(other.actor.x - x) < 10:
            distance_y = abs(other.actor.y - y)
            if distance_y < safe_distance:
                return False
    return True


def check_vehicle_distance(vehicle, min_distance=100):
    for other in random_vehicles:
        if other is not vehicle:
            if abs(other.actor.x - vehicle.actor.x) < 10:
                if abs((other.actor.y + other.rect().height) - (vehicle.actor.y)) < min_distance:
                    return True, other
    return False, None

#================================================================================#
# Collision
#================================================================================#
def get_collision_side(player_rect, other_rect):
    # Calcula sobreposição
    dx = (player_rect.centerx - other_rect.centerx)
    dy = (player_rect.centery - other_rect.centery)

    combined_half_widths = (player_rect.width + other_rect.width) / 2
    combined_half_heights = (player_rect.height + other_rect.height) / 2

    overlap_x = combined_half_widths - abs(dx)
    overlap_y = combined_half_heights - abs(dy)

    if overlap_x < overlap_y:
        # Colisão nas laterais
        if dx > 0:
            return "left" 
        else:
            return "right"  
    else:
        # Colisão na frente ou atrás
        if dy > 0:
            return "top"
        else:
            return "bottom"

#================================================================================#
def get_collision_point(rect1, rect2):
    
    overlap = rect1.clip(rect2)
    
    if overlap.width > 0 and overlap.height > 0:
        cx = int(overlap.x + overlap.width / 2)
        cy = int(overlap.y + overlap.height / 2)
        return (cx, cy)

    cx = int((rect1.centerx + rect2.centerx) / 2)
    cy = int((rect1.centery + rect2.centery) / 2)
    return (cx, cy)
