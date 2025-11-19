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
    
    game_state = "menu"  # "menu", "playing"
    current_level_index = 0
    world = None   
    hud = HUD(None, settings)
    running = True
    
    def restart_game(): 
        nonlocal world, current_level_index
        player_health = settings.get_player_health()
        world = World(
            LEVELS[current_level_index], 
            bg_path=LEVEL_BGS[current_level_index], 
            level_id=current_level_index,
            player_health=player_health
        )
        hud.player = world.player

    def start_new_game():
        nonlocal world, current_level_index
        current_level_index = 0
        player_health = settings.get_player_health()
        world = World(
            LEVELS[current_level_index], 
            bg_path=LEVEL_BGS[current_level_index], 
            level_id=current_level_index,
            player_health=player_health
        )
        hud.player = world.player
        print(f"Starting game - Difficulty: {settings.difficulty}, Health: {player_health}")  # Debug, có thể xóa sau

    while running:
        dt = clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Xử lý hover chuột
            if event.type == pygame.MOUSEMOTION:
                hud.update_hover(event.pos)

            if game_state == "menu":
                result = hud.handle_menu_input(event)
                if result == "start_game":
                    start_new_game()
                    game_state = "playing"
                elif result == "quit":
                    running = False
                    
            elif game_state == "playing":
                # Xử lý phím ESC
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    print("ESC pressed - Quay về menu chính")
                    game_state = "menu"
                
                # Xử lý click chuột vào nút settings
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hud.check_settings_click(event.pos):
                        print("Click bánh răng cưa - Quay về menu chính")
                        game_state = "menu"
                
                # Xử lý phím R khi player chết
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and world.player.dead:
                    restart_game()
        
        # Gameplay
        if game_state == "playing" and world:
            keys = pygame.key.get_pressed()

            world.player.handle_input(keys)
            world.player.apply_gravity()
            world.player.move_and_collide(world.solids())
            world.update()

            # Xử lý checkpoint - CHỈ cho phép chuyển level nếu chưa vượt quá số level cho phép
            max_levels = settings.get_max_levels()
            for cp in world.checkpoints:
                if cp.activated and keys[pygame.K_RETURN]:
                    if current_level_index < max_levels - 1:  # Chưa đạt level cuối
                        current_level_index += 1
                        player_health = world.player.health  # Giữ nguyên máu hiện tại
                        world = World(
                            LEVELS[current_level_index], 
                            bg_path=LEVEL_BGS[current_level_index],
                            level_id=current_level_index,
                            player_health=player_health
                        )
                        hud.player = world.player
                        print(f"Advanced to Level {current_level_index + 1}")
                    else:
                        # Đã hoàn thành tất cả level
                        print("Game Completed!")
                        game_state = "menu"
                    break
            
            # Update animation
            if world.player.health > 0:
                world.player.update_animation()
            else:
                world.player.update_death_animation()
        
        # Drawing
        screen.fill((0, 0, 0))
        
        if game_state == "playing" and world:
            world.draw_background(screen)
            world.draw(screen)
            hud.draw_ingame_hud(screen, current_level_index, len(LEVELS))

            if world.player.dead:
                death_text = hud.font.render("YOU DIED! Press R to restart", True, (255, 50, 50))
                death_rect = death_text.get_rect(center=(WIDTH//2, HEIGHT//2))
                screen.blit(death_text, death_rect)
        else:
            hud.draw_menu(screen)
        
        pygame.display.flip()

if __name__ == "__main__":
    run()
