class GameSettings:
    def __init__(self):
        self.difficulty = "NORMAL"  # EASY, NORMAL, HARD
        
    def get_max_levels(self):
        """Trả về số level tối đa cho độ khó"""
        if self.difficulty == "EASY":
            return 1
        elif self.difficulty == "NORMAL":
            return 2
        elif self.difficulty == "HARD":
            return 6
        return 1
    
    def get_display_max(self):
        if self.difficulty == "EASY":
            return 1
        elif self.difficulty == "NORMAL":
            return 2
        elif self.difficulty == "HARD":
            return 5
    
    def get_player_health(self):
        """Trả về máu ban đầu cho player"""
        if self.difficulty == "EASY":
            return 5
        elif self.difficulty == "NORMAL":
            return 4
        elif self.difficulty == "HARD":
            return 3
        return 1
    
    def apply_difficulty(self, player=None):
        """Áp dụng độ khó cho game"""
        if player:
            player.health = self.get_player_health()