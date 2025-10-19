# pyright: reportUndefinedVariable=false
import pgzrun
from pgzero import music

from game import *
from settings import *

game_state = "menu"

player = None
current_vehicle_index = 0

crash_sounds = [sounds.crash1, sounds.crash2, sounds.crash3, sounds.crash4]

#================================================================================#
# Update Loop
#================================================================================#
def update(dt):
    global game_state, crash, previous_crash

    if game_state == "menu":
        return
    
    elif game_state == "playing":
        state_result, crashes_this_frame = update_game(dt, keyboard)

        for _ in range(crashes_this_frame):
            play_crash_sound()

        if state_result == "game_over":
            game_state = "game_over"
        
        update_background_sound()

#================================================================================#
# Draw Loop
#================================================================================#
def draw():
    screen.clear()

    if game_state == "menu":
        screen.blit("main-menu", (0, 0))

    elif game_state == "select_vehicle":
        screen.blit("garage", (0, 0))

        current_vehicle = Actor(CAR_IMAGES_FOR_SELECTOR[current_vehicle_index])
        current_vehicle.pos = (WIDTH // 2, HEIGHT // 2)
        current_vehicle.draw()

    elif game_state == "playing":
        draw_game(screen)
    
    elif game_state == "paused":
        draw_game(screen)
        # screen.draw.filled_rect(Rect((0, 0), (WIDTH, HEIGHT)), (0, 0, 20, 50))
        screen.blit("menu-bg", (0, 0))
        screen.draw.text("JOGO PAUSADO", center=(WIDTH/2, 350), fontsize=60, color="white")
        screen.draw.text("Pressione ENTER para continuar", center=(WIDTH/2, 420), fontsize=35)
        screen.draw.text("ESC para voltar ao menu", center=(WIDTH/2, 470), fontsize=30, color="gray")
    
    elif game_state == "game_over":
        draw_game(screen)
        screen.blit("menu-bg", (0, 0))
        screen.blit("game-over-1", (0, 0))

#================================================================================#
# Draw vehicle selector
#================================================================================#
def draw_vehicle_selection(screen):
    screen.blit("garage-700-900", (0, 0))

    current_vehicle = Actor(CAR_IMAGES_FOR_SELECTOR[current_vehicle_index])
    current_vehicle.pos = (WIDTH // 2, HEIGHT // 2)
    current_vehicle.draw()

#================================================================================#
# Input
#================================================================================#
def on_key_down(key):
    global game_state, player, sound, current_vehicle_index

    if game_state == "menu":
        if key == keys.RETURN:
            game_state = "select_vehicle"
        elif key == keys.M:
            sound = not sound
            if sound:
                start_music()
            else:
                music.stop()

        elif key == keys.ESCAPE:
            exit()

    elif game_state == "select_vehicle":
        if key == keys.UP:
            current_vehicle_index = (current_vehicle_index - 1) % len(CAR_IMAGES_FOR_SELECTOR)
        elif key == keys.DOWN:
            current_vehicle_index = (current_vehicle_index + 1) % len(CAR_IMAGES_FOR_SELECTOR)
        elif key == keys.RETURN:
            player = start_game(current_vehicle_index)
            game_state = "playing"
        elif key == keys.ESCAPE:
            game_state = "menu"

    elif game_state == "playing":
        if key == keys.ESCAPE:
            game_state = "paused"
            update_background_sound()

    elif game_state == "paused":
        if key == keys.RETURN:
            game_state = "playing"
        elif key == keys.ESCAPE:
            game_state = "menu"

    elif game_state == "game_over":
        if key == keys.RETURN:
            player = start_game(current_vehicle_index)
            game_state = "playing"
        elif key == keys.ESCAPE:
            game_state = "menu"

#================================================================================#
# Music & Sounds
#================================================================================#

def start_music():
    if sound:
        music.play(current_music)
        music.set_volume(0.7)

def play_crash_sound():
    if sound:
        random.choice(crash_sounds).play().set_volume(0.4)

def update_background_sound():
    global bg_sound_1, bg_sound_2, bg_sound_1_active, bg_sound_2_active
    
    if sound and bg_sound_1_active is False: 
        sounds.bg_sound_1.play(-1).set_volume(0.5) 
        bg_sound_1_active = True 
    
    if sound and bg_sound_2_active is False: 
        sounds.bg_sound_2.play(-1).set_volume(0.5) 
        bg_sound_2_active = True 
    
    if (bg_sound_1_active or bg_sound_2_active) and (game_state == "paused" or game_state == "game_over"):      
        sounds.bg_sound_1.stop() 
        sounds.bg_sound_2.stop()
        bg_sound_1_active = False
        bg_sound_2_active = False

start_music()
pgzrun.go()