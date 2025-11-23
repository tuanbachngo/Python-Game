import pygame
# ------------------------------
# HÀM LOAD FRAME
# ------------------------------
def load_frames(sheet_path, frame_w, frame_h, num_frames):
    sheet = pygame.image.load(sheet_path).convert_alpha()
    frames = []
    for i in range(num_frames):
        frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), pygame.Rect(i*frame_w, 0, frame_w, frame_h))
        frames.append(frame)
    return frames