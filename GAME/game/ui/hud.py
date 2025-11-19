import pygame
from .menu import MenuManager
from config import asset
from ..core.constants import WIDTH, HEIGHT
# ------------------------------
# CLASS HUD
# ------------------------------
class HUD:
    def __init__(self, player, settings):
        self.player = player
        self.settings = settings
        self.font = pygame.font.Font(asset("super_mario_bros_2.ttf"), 12)
        
        # Menu manager
        self.menu_manager = MenuManager(WIDTH, HEIGHT)

        self.settings_icon = pygame.image.load(asset("gear.png")).convert_alpha()
        self.settings_icon_hover = self.create_hover_effect() 
        self.settings_button_rect = pygame.Rect(WIDTH - 48 - 50, 48, 48, 48)
        self.is_hovered = False

    def create_hover_effect(self):
        """Tạo hiệu ứng hover bằng cách làm sáng ảnh"""
        hover_icon = self.settings_icon.copy()
        # Tạo một surface màu trắng bán trong suốt
        highlight = pygame.Surface((48, 48), pygame.SRCALPHA)
        highlight.fill((160, 210, 225, 30))  # Trắng với độ trong suốt
        hover_icon.blit(highlight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return hover_icon 
             
    def check_settings_click(self, mouse_pos):
        """Kiểm tra click vào nút settings"""
        return self.settings_button_rect.collidepoint(mouse_pos)
    
    def update_hover(self, mouse_pos):
        """Cập nhật trạng thái hover"""
        self.is_hovered = self.settings_button_rect.collidepoint(mouse_pos)
    
    def draw_ingame_hud(self, surface, current_level, total_levels):
        # Tạo chuỗi thông tin trên 1 dòng
        info_text = f"Health: {self.player.health} | Level: {current_level + 1}/{total_levels} | Difficulty: {self.settings.difficulty}"
        text_surf = self.font.render(info_text, True, (255, 255, 255))  

        bg_x = (WIDTH - text_surf.get_width()) // 2 - 10  # Cách trái 60px
        bg_y = 20  # Cách trên 60px
        bg_rect = pygame.Rect(bg_x, bg_y, text_surf.get_width() + 10, text_surf.get_height() + 6)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))  # Đen với alpha 50%
        surface.blit(s, bg_rect)
        
        text_x = bg_x + 5
        text_y = bg_y + 3   
        surface.blit(text_surf, (text_x, text_y))
        
        # Vẽ nút settings với hiệu ứng hover
        current_icon = self.settings_icon_hover if self.is_hovered else self.settings_icon
        surface.blit(current_icon, self.settings_button_rect)
        
    def draw_menu(self, surface):
        self.menu_manager.draw(surface, self.settings.difficulty)
    
    def handle_menu_input(self, event):
        return self.menu_manager.handle_input(event, self.settings)