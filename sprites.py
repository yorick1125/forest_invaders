import pygame 
import spritesheet

pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Spritesheets')
BG = (50, 50, 50)
BLACK = (0, 0, 0)
spriteseet_image = pygame.image.load('doux.png').convert_alpha()
sprite_sheet = spritesheet.SpriteSheet(spriteseet_image)

frame_list = []
frame_steps = [4, 6, 3, 4]
action = 0
step_counter = 0

# first four frames are for idle animation
for frame in frame_steps:
    temp_list = []
    for _ in range(frame):
        temp_list.append(sprite_sheet.get_image(step_counter, 24, 24, 3, BLACK))
        step_counter += 1
    frame_list.append(temp_list)
    
# frame list = [
# Idle: [image1, image2, image3, image4]
# Run: [image1, image2, image3, image4, image5, image6]
# Stutter: [image1, image2, image3]
# Damage: [image1, image2, image3, image4]
# ]



update_time = pygame.time.get_ticks()
index = 0
ANIMATION_COOLDOWN = 100
run = True
while run:

    # update background
    screen.fill(BG)

    # update animation time
    if pygame.time.get_ticks() - update_time > ANIMATION_COOLDOWN:
        index = (index + 1) % len(frame_list)
        update_time = pygame.time.get_ticks()
        if index >= len(frame_list[action]):
            index = 0

    # display image
    screen.blit(pygame.transform.flip(frame_list[action][index], True, False), (0, 0))

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN and action > 0:
                action -= 1
                index = 0
            if event.key == pygame.K_UP and action < len(frame_list) - 1:
                action += 1
                index = 0
            
        


    
    pygame.display.update()

pygame.quit()