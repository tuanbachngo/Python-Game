# Stage 0: Tạo không gian cho game 

import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((600, 375)) # tạo màn hình game theo kích thước
pygame.display.set_caption('Ping 1: Adventure') # caption xuất hiện trên màn hình
clock = pygame.time.Clock()
font = pygame.font.Font("D:\Python NEU\PixelifySans-VariableFont_wght.ttf", 30) # down font mình muốn về vè copy path paste 

sky_surface = pygame.image.load('sky.jpg') 
ground_surface = pygame.image.load('grd.png')
text = font.render('my game', False, 'Yellow') # False là chữ răng cưa, True là chữ mượt 
player = pygame.image.load("D:\Python NEU\pngtree-yellow-pixel-duck-cartoon-decorative-element-png-image_16986838.webp")
player_main = pygame.transform.smoothscale(player,(40,45))
while True:
    for event in pygame.event.get(): # chạy các sự kiện trong game, kiểm tra các sự kiện
        if event.type == pygame.QUIT: # quit nếu gặp các common thao tác như bấm enter, click chuột, ấn phím bất kỳ, ấn X, so on...
            pygame.quit()
            exit()
    screen.fill((25, 28, 35)) # tô màu màn hình theo các sắc độ màu (RED,GREEN,BLUE, max là 255, từ đó tự trộn màu)
    screen.blit(sky_surface, (0, 0)) # load ảnh lên màn hình tính từ top left corner, các tọa độ khác tự ước tính theo set mode 
    screen.blit(ground_surface,(0,250)) # đặt ảnh ở điểm tọa độ y là 250 bên dưới
    screen.blit(text, (240,30))
    screen.blit(player_main,(5,210))
    
    pygame.display.flip() # update lên màn hình chính
    # làm thêm phần chuyển động animations, trái phải 
pygame.quit()
