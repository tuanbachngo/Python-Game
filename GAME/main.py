import pygame
from game.core import WIDTH, HEIGHT, FPS, GameSettings, LEVELS, LEVEL_BGS
from game.ui import HUD
from game.world import World 
# ------------------------------
# HÀM CHẠY GAME CHÍNH
# ------------------------------
def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trap Adventure")
    clock = pygame.time.Clock()
    
    # Khởi tạo
    settings = GameSettings()
    game_state = "menu"  # "menu", "playing", "game_over", "win"
    current_level_index = 0
    world = None   
    hud = HUD (None, settings)
    running = True
    delay = 0

    # Trạng thái nhạc
    menu_music_playing = False
    game_music_playing = False

    def restart_game(): 
        nonlocal world, current_level_index, delay
        delay = 0
        player_health = settings.get_player_health()
        world = World(
            LEVELS[current_level_index], 
            bg_path=LEVEL_BGS[current_level_index], 
            level_id=current_level_index,
            player_health=player_health
        )
        hud.player = world.player
        hud.stop_menu_music()  
        hud.play_game_music()

    def start_new_game():
        nonlocal world, current_level_index, delay
        current_level_index = 0
        player_health = settings.get_player_health()
        delay = 0
        world = World(
            LEVELS[current_level_index], 
            bg_path=LEVEL_BGS[current_level_index], 
            level_id=current_level_index,
            player_health=player_health
        )
        hud.player = world.player
        hud.stop_menu_music()  
        hud.play_game_music()
        
    while running:
        dt = clock.tick(FPS)
        current = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Xử lý hover chuột
            if event.type == pygame.MOUSEMOTION:
                hud.update_hover(event.pos)

            if game_state == "menu":
                if not menu_music_playing:
                    hud.play_menu_music()
                    menu_music_playing = True
                    hud.stop_game_music()
                    game_music_playing = False

                result = hud.handle_menu_input(event)
                if result == "start_game":
                    start_new_game()
                    game_state = "playing"
                elif result == "quit":
                    running = False
                    
            elif game_state == "playing":
                if not game_music_playing:
                    hud.play_game_music()
                    game_music_playing = True
                    hud.stop_menu_music()
                    menu_music_playing = False

                # Xử lý phím ESC
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                
                # Xử lý click chuột vào nút settings
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hud.check_settings_click(event.pos):
                        game_state = "menu"
                
                # Xử lý phím R khi player chết
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and world.player.dead:
                    restart_game()

            elif game_state == "game_over":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    restart_game()
                    game_state = "playing"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_state = "menu"     

            elif game_state == "win":
                if game_music_playing:
                    hud.stop_game_music()
                    game_music_playing = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        start_new_game()
                        game_state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "menu"

        # Gameplay
        if game_state == "playing" and world:
            keys = pygame.key.get_pressed()

            world.player.handle_input(keys)
            world.player.apply_gravity()
            world.player.move_and_collide(world.solids())
            world.update(dt)

            max_levels = settings.get_max_levels()
            
            for cp in world.checkpoints:
                if cp.activated and not world.player.dead:
                    if not hasattr(cp, "sound_played"):
                        cp.sound_played = False
                    if not cp.sound_played:
                        hud.play_checkpoint_sound()
                        cp.sound_played = True
                    if current_level_index < max_levels - 1:                        
                        current_level_index += 1
                        delay = 0                       
                        player_health = world.player.health

                        if world and world.player:
                            world.player.stop_running_sound()

                        world = World(
                                LEVELS[current_level_index],
                                bg_path=LEVEL_BGS[current_level_index],
                                level_id=current_level_index,
                                player_health=player_health
                            )
                        hud.player = world.player
                        hud.stop_game_music()
                        hud.play_game_music()

                    else:
                        if world.player.health <= 0 and delay == 0:
                                delay = current
                        if current - delay > 700:
                                game_state = "win"
                    break
            
            if world.player.health <= 0:
                if delay == 0:
                    delay = current
                    hud.stop_game_music()
                    hud.play_game_over_sound()
                world.player.update_death_animation()
                if current - delay > 700:
                    game_state = "game_over"
            else:
                world.player.update_animation()
        
        # Drawing
        screen.fill((0, 0, 0))
        
        if game_state == "playing" and world:
            world.draw_background(screen)
            world.draw(screen)
            hud.draw_ingame_hud(screen, current_level_index)

        elif game_state == "game_over" and world:
            # Vẽ game đóng băng ở background
            world.draw_background(screen)
            world.draw(screen)
            
            # Vẽ overlay game over
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Đen bán trong suốt
            screen.blit(overlay, (0, 0))
            
            game_over_text = hud.font.render("GAME OVER", True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(game_over_text, game_over_rect)
            
            restart_text = hud.font.render("Press R to Restart or ESC for Main Menu", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)

        elif game_state == "win" and world:
            # Vẽ game đóng băng ở background
            world.draw_background(screen)
            world.draw(screen)
            
            win_text = hud.font.render("WINNER", True, (255, 0, 0))
            win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(win_text, win_rect)
            
            restart_text = hud.font.render("Press ESC for Main Menu", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)
            
        else:
            hud.draw_menu(screen)
        
        pygame.display.flip()

if __name__ == "__main__":
    run()
