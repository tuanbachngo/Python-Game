import pygame
from .menu import MenuManager
from config import asset
from ..core.constants import WIDTH, HEIGHT

class HUD:
    def __init__(self, player, settings):
        self.player = player
        self.settings = settings
        self.font = pygame.font.Font(asset("super_mario_bros_2.ttf"), 12)
        
        # Menu manager
        self.menu_manager = MenuManager(WIDTH, HEIGHT)

        self.settings_icon = pygame.image.load(asset("gear.png")).convert_alpha()
        self.settings_icon_hover = self.create_hover_effect() 
        self.settings_button_rect = pygame.Rect(5, 0, 48, 48)
        self.is_hovered = False

        self.HUD_MAPPING = {
            0: 1,
            1: 2,
            2: 3,
            3: 4,
            4: 5,
            5: 5   # hoặc 5 hoặc bất cứ gì bạn muốn
        }  

        self.menu_music = pygame.mixer.Sound(asset("openning_sound.mp3"))  # chuyển sang .wav
        self.menu_music.set_volume(0.8)
        self.menu_channel = pygame.mixer.Channel(0)
        self.menu_playing = False
            # Nhạc gameplay
        self.game_music = pygame.mixer.Sound(asset("game-music.mp3"))
        self.game_music.set_volume(0.8)
        self.game_music_channel = pygame.mixer.Channel(3)
        self.game_music_playing = False
            # Nhạc game over
        self.game_over_sound = pygame.mixer.Sound(asset("dead_sound.mp3"))
        self.game_over_sound.set_volume(0.5)
            #Nhạc checkpoint
        self.checkpoint_channel = pygame.mixer.Channel(4)
        self.checkpoint_sound = pygame.mixer.Sound(asset("checkpoint_sound.mp3"))
        self.checkpoint_sound.set_volume(0.7)
            #Nhạc spike trap
        self.spike_channel = pygame.mixer.Channel(5)
        self.spike_sound = pygame.mixer.Sound(asset("trap_sound.mp3"))
        self.spike_sound.set_volume(0.7) 

    def play_menu_music(self):
        if self.menu_music and not self.menu_playing:
            self.menu_channel.play(self.menu_music, loops=-1)
            self.menu_playing = True

    def stop_menu_music(self):
        if self.menu_music and self.menu_playing:
            self.menu_channel.stop()
            self.menu_playing = False
            
        # --- Nhạc gameplay ---
    def play_game_music(self):
        if self.game_music and not self.game_music_playing:
            self.game_music_channel.play(self.game_music, loops=-1)
            self.game_music_playing = True
        if self.menu_playing:
            self.menu_channel.stop()
            self.menu_playing = False

    def stop_game_music(self):
        if self.game_music_playing:
            self.game_music_channel.stop()
            self.game_music_playing = False
        
        # --- Nhạc game over ---
    def play_game_over_sound(self):
        if self.game_over_sound:
            self.game_music_channel.stop()
            self.game_music_playing = False
            self.game_music_channel.play(self.game_over_sound)  
        
    def play_checkpoint_sound(self):
        if self.checkpoint_sound:
            self.checkpoint_channel.play(self.checkpoint_sound)
    
    def play_spike_sound(self):
        if self.spike_sound:
            if not self.spike_channel.get_busy():  # Chỉ play nếu chưa bận
                self.spike_channel.play(self.spike_sound, loops=-1)

    def stop_spike_sound(self):
        if self.spike_channel.get_busy():
            self.spike_channel.stop()

    def create_hover_effect(self):
        hover_icon = self.settings_icon.copy()
        highlight = pygame.Surface((48, 48), pygame.SRCALPHA)
        highlight.fill((160, 210, 225, 5))
        hover_icon.blit(highlight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return hover_icon 
             
    def check_settings_click(self, mouse_pos):
        """Kiểm tra click vào nút settings"""
        return self.settings_button_rect.collidepoint(mouse_pos)
    
    def update_hover(self, mouse_pos):
        """Cập nhật trạng thái hover"""
        self.is_hovered = self.settings_button_rect.collidepoint(mouse_pos)
    
    def draw_ingame_hud(self, surface, current_level):
        display_level = self.HUD_MAPPING[current_level]
        display_max   = self.settings.get_display_max()
        info_text = f"Health: {self.player.health} | Level: {display_level}/{display_max} | Difficulty: {self.settings.difficulty}"
        text_surf = self.font.render(info_text, True, (255, 255, 255))  

        bg_x = (WIDTH - text_surf.get_width()) // 2 - 10 
        bg_y = 20  
        bg_rect = pygame.Rect(bg_x, bg_y, text_surf.get_width() + 10, text_surf.get_height() + 6)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))  # Đen với alpha 50%
        surface.blit(s, bg_rect)
        
        text_x = bg_x + 5
        text_y = bg_y + 3   
        surface.blit(text_surf, (text_x, text_y))

        current_icon = self.settings_icon_hover if self.is_hovered else self.settings_icon
        surface.blit(current_icon, self.settings_button_rect)
        
    def draw_menu(self, surface):
        self.menu_manager.draw(surface, self.settings.difficulty)
    
    def handle_menu_input(self, event):
        return self.menu_manager.handle_input(event, self.settings) # encapsulate method, menu manager nhận giá trị, gửi về HUD, rồi HUD gửi về main.py