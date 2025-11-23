import pygame
from ..core.constants import WIDTH
from config import asset

class MenuManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font_large = pygame.font.Font(asset("super_mario_bros_2.ttf"), 36)
        self.font_medium = pygame.font.Font(asset("super_mario_bros_2.ttf"), 24)
        self.font_small = pygame.font.Font(asset("super_mario_bros_2.ttf"), 15)
        self.background_image = pygame.image.load(asset("bg-2.png")).convert()

        self.title_color = (0, 0, 0)    
        self.selected_color = (0, 0, 0) 
        self.normal_color = (80, 80, 80)  
        self.highlight_color = (0, 100, 200) 
        self.help_color = (80, 80, 80)  
        
        self.main_menu_options = ["START GAME", "DIFFICULTY", "QUIT"]
        self.difficulty_options = ["EASY", "NORMAL", "HARD"]
        self.difficulty_descriptions = {
            "EASY": "1 Level, 5 Health",
            "NORMAL": "2 Levels, 4 Health", 
            "HARD": "5 Levels, 3 Health"
        } 

        self.selected_index = 0
        self.current_menu = "main"  
        self._item_rects = []

    def render_center(self, surface, font, text, y, color):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, y))
        surface.blit(surf, rect)
        return rect # Trả về rect để sử dụng cho việc phát hiện va chạm chuột
    
    def draw (self, surface, current_difficulty):
        surface.blit(self.background_image, (0, 0)) # Vẽ nền menu ở góc trên bên trái
        self._item_rects = [] # Reset danh sách rect mỗi lần vẽ lại menu

        if self.current_menu == "main":
            self.render_center(surface, self.font_large, "BIRD ADVENTURE", 120, self.title_color) # vẽ tiêu đề ở vị trí Y = 120px
            base_y = 250
            for i, label in enumerate(self.main_menu_options): # vòng lặp options
                color = self.selected_color if i == self.selected_index else self.normal_color  
                rect = self.render_center(surface, self.font_medium, label, base_y + i * 80, color)
                self._item_rects.append(rect)
            # lưu rect của từng option để phát hiện va chạm chuột
                if i == self.selected_index:
                    surface.blit(self.font_medium.render(">", True, self.selected_color), (rect.left - 40, rect.y))
        else:
            self.render_center(surface, self.font_medium, "SELECT DIFFICULTY", 100, self.title_color)
            base_y = 200
            for i, label in enumerate(self.difficulty_options):
                if i == self.selected_index:
                    color = self.selected_color
                elif label == current_difficulty:
                    color = self.highlight_color  # độ khó đang áp dụng
                else:
                    color = self.normal_color

                rect = self.render_center(surface, self.font_medium, label, base_y + i * 80, color)
                self._item_rects.append(rect)
                self.render_center(surface, self.font_small, self.difficulty_descriptions[label], rect.centery + 30, self.help_color)
                if i == self.selected_index:
                    surface.blit(self.font_medium.render(">>", True, self.selected_color),(rect.left - 60, rect.y))

            self.render_center(surface, self.font_small, "ENTER: Select  |  ESC: Back", self.screen_height - 50, self.help_color)
                
    def handle_mouse_hover(self, mouse_pos):
        """Highlight option khi di chuột qua"""
        if self.current_menu == "main":
            for i, rect in enumerate(self._item_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    break
        else:  # difficulty menu
            for i, rect in enumerate(self._item_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    break

    def handle_main_menu_mouse(self, mouse_pos, settings):
        """Xử lý click chuột trên main menu"""
        for i, rect in enumerate(self._item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_index = i
                option = self.main_menu_options[i]

                if option == "START GAME":
                    return "start_game"
                elif option == "DIFFICULTY":
                    self.current_menu = "difficulty" # chyển sang menu difficulty
                    self.selected_index = self.difficulty_options.index(settings.difficulty) # trả về vị trí hiện tại tương ứng với độ khó (index của độ khó)
                elif option == "QUIT":
                    return "quit"
                
        return None

    def handle_difficulty_mouse(self, mouse_pos, settings): # settings được truyền vào như tham số
        """Xử lý click chuột trên difficulty menu"""
        for i, rect in enumerate(self._item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_index = i
                settings.difficulty = self.difficulty_options[i]
                settings.apply_difficulty() # vì settings là đối tượng đã tồn tại nên được gọi luôn phương thức không cần import lại từ core.settings
                self.current_menu = "main"
                self.selected_index = 1
                return None
        return None

    def handle_main_menu_input(self, event, settings):
        # event.key là phím được nhấn

        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.main_menu_options) # tạo hiệu ứng vòng lặp
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.main_menu_options)

        elif event.key == pygame.K_RETURN:
            selected_option = self.main_menu_options[self.selected_index]
            if selected_option == "START GAME":
                return "start_game"
            elif selected_option == "DIFFICULTY":
                self.current_menu = "difficulty"
                self.selected_index = self.difficulty_options.index(settings.difficulty)
            elif selected_option == "QUIT":
                return "quit"
                
        elif event.key == pygame.K_ESCAPE: # ESC để thoát khỏi game từ menu chính
            return "quit"
            
        return None

    def handle_difficulty_input(self, event, settings):
        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.difficulty_options)
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.difficulty_options)

        elif event.key == pygame.K_RETURN: # phím enter
            settings.difficulty = self.difficulty_options[self.selected_index]
            settings.apply_difficulty()
            self.current_menu = "main"
            self.selected_index = 1  # Quay lại mục Difficulty trong menu chính

        elif event.key == pygame.K_ESCAPE:
            self.current_menu = "main"
            self.selected_index = 1  # Quay lại mục Difficulty trong menu chính
        return None    
    
    def handle_input(self, event, settings):
        """Xử lý cả bàn phím và chuột"""
        # event.pos là vị trí con trỏ chuột
        # event.type là kiểu sự kiện (di chuyển chuột, click chuột, nhấn phím,...)

        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_hover(event.pos) # highlight option khi di chuột qua

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Click trái
            if self.current_menu == "main":
                return self.handle_main_menu_mouse(event.pos, settings) # xử lý click chuột trên main menu
            else:
                return self.handle_difficulty_mouse(event.pos, settings) # xử lý click chuột trên difficulty menu
        
        if event.type == pygame.KEYDOWN:
            if self.current_menu == "main":
                return self.handle_main_menu_input(event, settings)
            else:
                return self.handle_difficulty_input(event, settings)
        return None