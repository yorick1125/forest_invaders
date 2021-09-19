import pygame, enum, os, button, spritesheet, random
from pygame import draw, encode_file_path
from pygame import sprite


# INITIALIZATION
#-----------------------------------------------------------------------------------------
pygame.init()

clock = pygame.time.Clock()
FPS = 60
game_over = 0
seconds_left = 40
timer = pygame.time.get_ticks()

# load music and sounds
pygame.mixer.music.load('audio/Hidden_Highland_Remix.wav')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

# game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
FLOOR_POSITION = 500
GRAVITY = 0.75
SCROLL_THRESH = 200

# scroll settings
bg_scroll = 0
screen_scroll = 0

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Forest')

font_L = pygame.font.SysFont('arialblack', 45)
font_M = pygame.font.SysFont('arialblack', 20)
pokeFont = pygame.font.Font("Pokemon GB.ttf", 16)
arial = pygame.font.Font(None, 45)
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# IMAGES
#-----------------------------------------------------------------------------------------
# menu
menu_bg = pygame.image.load('img/menu/bg.jpg')
menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
start_img = pygame.image.load('img/menu/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/menu/exit_btn.png').convert_alpha()
victory_img = pygame.image.load('img/icons/victory.png').convert_alpha()
defeat_img = pygame.image.load('img/icons/defeat.png').convert_alpha()
restart_img = pygame.image.load('img/icons/restart.png').convert_alpha()

# background
sky = pygame.image.load('img/Background/Sky.png').convert_alpha()
bg_decor = pygame.image.load('img/Background/BG_Decor.png').convert_alpha()
middle_decor = pygame.image.load('img/Background/Middle_Decor.png').convert_alpha()
foreground = pygame.image.load('img/Background/Foreground.png').convert_alpha()
ground = pygame.image.load('img/Background/Ground.png').convert_alpha()
floor = pygame.image.load('img/Background/floor.png').convert_alpha()
floor = pygame.transform.scale(floor, (sky.get_width() + 5, floor.get_height()))

# FUNCTIONS
#-----------------------------------------------------------------------------------------
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_centered_text(text, font, color, x, y, largeFont):
    if largeFont:
        img = font_L.render(text, True, color)
    else:
        img = font_M.render(text, True, color)
    img_rect = img.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    img_rect.y = y
    screen.blit(img, img_rect)

def draw_score(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_bg():
    width = sky.get_width()
    for i in range(1000):
        screen.blit(sky, ((i * width) - bg_scroll * 0.5, 0))
        screen.blit(bg_decor, ((i * width) - bg_scroll * 0.6, SCREEN_HEIGHT - bg_decor.get_height() - 300))
        screen.blit(middle_decor, ((i * width) - bg_scroll * 0.7, SCREEN_HEIGHT - middle_decor.get_height() - 150))
        screen.blit(foreground, ((i * width) - bg_scroll * 0.8, SCREEN_HEIGHT - foreground.get_height()))
        screen.blit(ground, ((i * width) - bg_scroll * 0.8, SCREEN_HEIGHT - ground.get_height()))
        screen.blit(floor, ((i * width) - bg_scroll * 0.8, SCREEN_HEIGHT - (SCREEN_HEIGHT - FLOOR_POSITION) - 30))

def draw_menu_bg():
    screen.blit(menu_bg, (0, 0))


# CLASSES
#-----------------------------------------------------------------------------------------
class Velocity():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Direction(enum.Enum):
    Right = 1
    Left = -1
    Null = 0

class Player(pygame.sprite.Sprite):
    def __init__(self, name, x, y, width, height, health, flipped):
        super().__init__()

        # variables
        self.moving_right = False
        self.moving_left = False
        self.alive = True
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.flipped = flipped
        self.direction = 0
        self.acceleration = 1
        self.velocity = Velocity(0, 0)
        self.in_air = False
        self.jump = False
        self.attacking = False
        self.sliding = False
        self.health = health
        self.max_health = health
        self.accel_timer = pygame.time.get_ticks()
        self.speed = 10


        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        self.hurt = False
        self.recoil = False
        self.recoil_counter = 0
        self.bounce = False
        self.hit_count = 0


        # animation variables
        self.frame_index = 0
        self.animation_list = []
        self.action = 0
        self.update_time = pygame.time.get_ticks() # date.now()
        
        if self.name == 'mummy':
            self.generate_mummy_animation_list()
        elif self.name == 'adventurer' or self.name == 'fem_warrior':
            self.generate_player_animation_list()
            self.direction = 1
        elif self.name == 'snake':
            self.generate_snake_animation_list()
            self.direction = -1


        self.img = self.animation_list[self.action][self.frame_index]
        self.rect = self.img.get_rect()
        self.rect.center = (x, y)


    def generate_player_animation_list(self):
        # animation images
        animations = ['Idle', 'Attack', 'Run', 'Crouch', 'Jump', 'Fall', 'Slide', 'Hurt', 'Death']
        for animation in animations:
            # reset temporary list of images
            temp_list = []
            # get number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.name}/{animation}'))
            # loop through each image/frame for the animations
            for i in range(num_of_frames):
                image = pygame.image.load(f'img/{self.name}/{animation}/{i}.png')
                image = pygame.transform.scale(image, (self.width, self.height))
                temp_list.append(image)
            self.animation_list.append(temp_list)

        # frame list = [
        # Idle: [image1, image2, image3, image4]
        # Attack: [image1, image2, image3]
        # Run: [image1, image2, image3, image4, image5, image6]
        # Etc...
        # ]

    def generate_mummy_animation_list(self):
        # animation images
        # 0: Idle
        # 1: Attack
        # 2: Walk
        # 3: Hurt
        # 4: Death


        frame_steps = [4, 6, 6, 6]

        # Idle
        idle_images = pygame.image.load('img/mummy/Mummy_Idle.png').convert_alpha()
        idle_spritesheet = spritesheet.SpriteSheet(idle_images)
        temp_list = []
        step_counter = 0
        for _ in range(frame_steps[0]):
            img = idle_spritesheet.get_image(step_counter, 48, 48, 3, BLACK)
            temp_list.append(img)
            step_counter += 1
        self.animation_list.append(temp_list)

        # Attack
        attack_images = pygame.image.load('img/mummy/Mummy_attack.png').convert_alpha()
        attack_spritesheet = spritesheet.SpriteSheet(attack_images)
        temp_list = []
        step_counter = 0
        for _ in range(frame_steps[1]):
            img = attack_spritesheet.get_image(step_counter, 48, 48, 3, BLACK)
            temp_list.append(img)
            step_counter += 1
        self.animation_list.append(temp_list)

        # Walk
        walk_images = pygame.image.load('img/mummy/Mummy_walk.png').convert_alpha()
        walk_spritesheet = spritesheet.SpriteSheet(walk_images)
        temp_list = []
        step_counter = 0
        for _ in range(frame_steps[2]):
            img = walk_spritesheet.get_image(step_counter, 48, 48, 3, BLACK)
            temp_list.append(img)
            step_counter += 1
        self.animation_list.append(temp_list)

        # Hurt
        hurt_images = pygame.image.load('img/mummy/Mummy_hurt.png').convert_alpha()
        hurt_spritesheet = spritesheet.SpriteSheet(hurt_images)
        temp_list = []
        step_counter = 0
        for _ in range(frame_steps[2]):
            img = hurt_spritesheet.get_image(step_counter, 48, 48, 3, BLACK)
            temp_list.append(img)
            step_counter += 1
        self.animation_list.append(temp_list)

        # Death
        death_images = pygame.image.load('img/mummy/Mummy_death.png').convert_alpha()
        death_spritesheet = spritesheet.SpriteSheet(death_images)
        temp_list = []
        step_counter = 0
        for _ in range(frame_steps[3]):
            img = death_spritesheet.get_image(step_counter, 48, 48, 3, BLACK)
            temp_list.append(img)
            step_counter += 1
        self.animation_list.append(temp_list)

        # frame list = [
        # Idle: [image1, image2, image3, image4]
        # Attack: [image1, image2, image3]
        # Run: [image1, image2, image3, image4, image5, image6]
        # Etc...
        # ]

    def generate_snake_animation_list(self):
        # animation images
        # 0: Idle
        # 1: Attack
        # 2: Walk
        # 3: Hurt
        # 4: Death


        frame_steps = [4, 6, 4, 2, 4]

        # Idle
        idle_images = pygame.image.load('img/snake/Snake_idle.png').convert_alpha()
        idle_spritesheet = spritesheet.SpriteSheet(idle_images)
        temp_list = []
        step_counter = 0
        for _ in range(frame_steps[0]):
            img = idle_spritesheet.get_image(step_counter, 48, 48, 3, BLACK)
            temp_list.append(img)
            step_counter += 1
        self.animation_list.append(temp_list)

        # Attack
        attack_images = pygame.image.load('img/snake/Snake_attack.png').convert_alpha()
        attack_spritesheet = spritesheet.SpriteSheet(attack_images)
        temp_list = []
        step_counter = 0
        for _ in range(frame_steps[1]):
            img = attack_spritesheet.get_image(step_counter, 48, 48, 3, BLACK)
            temp_list.append(img)
            step_counter += 1
        self.animation_list.append(temp_list)

        # Walk
        walk_images = pygame.image.load('img/snake/Snake_walk.png').convert_alpha()
        walk_spritesheet = spritesheet.SpriteSheet(walk_images)
        temp_list = []
        step_counter = 0
        for _ in range(frame_steps[2]):
            img = walk_spritesheet.get_image(step_counter, 48, 48, 3, BLACK)
            temp_list.append(img)
            step_counter += 1
        self.animation_list.append(temp_list)

        # Hurt
        hurt_images = pygame.image.load('img/snake/Snake_hurt.png').convert_alpha()
        hurt_spritesheet = spritesheet.SpriteSheet(hurt_images)
        temp_list = []
        step_counter = 0
        for _ in range(frame_steps[3]):
            img = hurt_spritesheet.get_image(step_counter, 48, 48, 3, BLACK)
            temp_list.append(img)
            step_counter += 1
        self.animation_list.append(temp_list)

        # Death
        death_images = pygame.image.load('img/snake/Snake_death.png').convert_alpha()
        death_spritesheet = spritesheet.SpriteSheet(death_images)
        temp_list = []
        step_counter = 0
        for _ in range(frame_steps[4]):
            img = death_spritesheet.get_image(step_counter, 48, 48, 3, BLACK)
            temp_list.append(img)
            step_counter += 1
        self.animation_list.append(temp_list)


        # frame list = [
        # Idle: [image1, image2, image3, image4]
        # Attack: [image1, image2, image3]
        # Run: [image1, image2, image3, image4, image5, image6]
        # Etc...
        # ]

    def update(self):
        self.update_animation()
        if self.attacking and self.name == "adventurer":
            self.update_action(1)
            enemies_attacked = pygame.sprite.spritecollide(player, enemy_group, False)
            if len(enemies_attacked) > 0:
                if enemies_attacked[0].alive:
                    self.attack(enemies_attacked[0])
        self.check_alive()

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        if self.action == 3 and self.name == 'snake':
            ANIMATION_COOLDOWN = 40

        # update image depending on current frame
        self.img = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

            # if animation has run out then reset back to the start
            if self.frame_index >= len(self.animation_list[self.action]):
                # only remove dying snake from its group after the animation is finished
                if self.action == 4 and self.name == "snake":
                    enemy_group.remove(self)
                if self.action == 3 and self.name == 'snake':
                    self.action = 0
                if self.action == 1 and self.name == "adventurer":
                    self.attacking = False
                    self.action = 0
                if self.action == len(self.animation_list) - 1 and self.name == 'snake':
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            # update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def move(self):
        # reset movement variables
        screen_scroll = 0
        # dx and dy represent the CHANGE in x and y
        dx = 0
        dy = 0

        # slow down if player is sliding
        if self.sliding:
            self.acceleration = 8
        else:
            self.acceleration = 10


        # assign movement variables if moving left or right
        if self.moving_left:
            dx = -self.speed
            self.flipped = True
            self.direction = -1
        if self.moving_right:
            dx = self.speed
            self.flipped = False
            self.direction = 1




        # jump
        if self.jump and not self.in_air:
            self.velocity.y = -11
            self.jump = False
            self.in_air = True

        # falling
        if self.velocity.y >= 0 and self.in_air:
            self.update_action(5) # Fall


        # apply gravity
        self.velocity.y += GRAVITY
        dy += self.velocity.y

        # check collision with floor
        if self.rect.bottom + dy > FLOOR_POSITION:
            if self.in_air:
                if self.moving_left or self.moving_right:
                    player.update_action(2) # moving
                else:
                    player.update_action(0) # idle
            dy = FLOOR_POSITION - self.rect.bottom
            self.in_air = False


        # check if going off the edges of the screen
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            dx = 0

        # update player rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.rect.right > SCREEN_WIDTH - SCROLL_THRESH or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
            self.rect.x -= dx
            screen_scroll = -dx

        return screen_scroll

    def enemy_move(self):
        # dx and dy represent the CHANGE in x and y
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if self.moving_left:
            dx = -self.speed
            self.flipped = True
            self.direction = -1
        if self.moving_right:
            dx = self.speed
            self.flipped = False
            self.direction = 1

        # check for recoil
        if self.name == "snake" and self.action == 3:
            self.hurt = True
            self.hit_count += 1

        # jump
        if self.jump and not self.in_air:
            self.velocity.y = -11
            self.jump = False
            self.in_air = True


        # Bounce
        if self.hit_count >= 3 and not self.in_air:
            #recoil vertically
            self.velocity.x = 2 * self.direction * (random.uniform(0.1, 3))
            self.velocity.y = -9 * (random.uniform(0.5, 1))
            self.bounce = False
            self.in_air = True
            self.hit_count = 0





        # apply gravity and recoil
        self.velocity.y += GRAVITY
        dx += self.velocity.x
        dy += self.velocity.y

        # check collision with floor
        if self.rect.bottom + dy > FLOOR_POSITION:
            dy = FLOOR_POSITION - self.rect.bottom
            self.in_air = False
            self.bounce = False
            self.velocity.y = 0
            self.velocity.x = 0

        # check if going off the edges of the screen
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            dx = 0

        # update ai rectangle position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

    def enemy(self):
        # Hit recoil
        if self.name == "snake" and self.action == 3:
            self.recoil = True
            self.rect.x += 10 * self.direction
            self.rect.y -= 5

        if self.alive and player.alive:
            if random.randint(1, 200) == 1 and not self.idling:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50

            # check if the ai is near the player
            if self.vision.colliderect(player.rect):
                # stop running and shoot the player 
                self.update_action(1) # 0: Idle
            # if ai doesnt see player
            else:
                if not self.idling:
                    if self.direction == 1:
                        self.moving_right = True
                    elif self.direction == -1:
                        self.moving_right = False
                    self.moving_left = not self.moving_right
                    self.enemy_move()
                    self.update_action(2) # walk
                    self.move_counter += 1

                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > 50   :
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    self.update_action(0)
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += screen_scroll

    def npc(self):
        if self.alive and player.alive:
            if random.randint(1, 200) == 1 and not self.idling:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 200


            if not self.idling:
                if self.direction == 1:
                    self.moving_right = True
                elif self.direction == -1:
                    self.moving_right = False
                self.moving_left = not self.moving_right
                self.enemy_move()
                self.update_action(2)
                self.move_counter += 1

                if self.move_counter > 30   :
                    self.direction *= -1
                    self.move_counter *= -1
            else:
                self.idling_counter -= 1
                if self.idling_counter <= 0:
                    self.idling = False

        # scroll
        self.rect.x += screen_scroll

    def attack(self, target):
        hit_range_rect = pygame.Rect(self.rect.left - 10, self.rect.top - 10, self.rect.width + 10, self.rect.height + 10)
        if hit_range_rect.colliderect(target.rect):
            target.update_action(3)
            target.health -= 3
            target.direction = random.randint(-1, 1)

    def draw(self):
        if self.flipped:
            screen.blit(pygame.transform.flip(self.img, True, False).convert_alpha(), self.rect)
        else:
            screen.blit(self.img, self.rect)

    def check_alive(self):
        if self.health <= 0:
            self.health = 0 
            self.acceleration = 0
            self.alive = 0
            self.action = len(self.animation_list) - 1
            return False
        else:
            return True

    def end_movement(self):
        player.update_action(0)
        player.moving_right = False
        player.moving_left = False

class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp

    def draw(self, hp):
        # update with new health
        self.hp = hp
        # calculate health ratio
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        super().__init__()
        self.image = pokeFont.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        # move damage text up
        self.rect.y -= 1

        # delete the text after a few seconds
        self.counter += 1

        if self.counter > 30:
            self.kill()

# BUTTONS 
# -----------------------------------------------------------------------------------------
# create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 50, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 200, exit_img, 1)
restart_button = button.Button(330, 150, restart_img, 0.6)
restart_button.rect.centerx = SCREEN_WIDTH // 2
victory_button = button.Button(330, 10, victory_img, 1 )
victory_button.rect.centerx = SCREEN_WIDTH // 2



# MENU 
# -----------------------------------------------------------------------------------------
start_game = False
while not start_game:
    draw_menu_bg()
    draw_centered_text("Welcome to Forest Invaders!", arial, (255, 255, 0), 40, 50, True)
    draw_centered_text("Created by Yorick-Ntwari Niyonkuru", arial, (255, 255, 0), 40, 175, False)
    draw_centered_text("You must save the magic forest from the ", arial, (255, 255, 0), 40, 200, False)
    draw_centered_text("invasion of snakes before time runs out!", arial, (255, 255, 0), 40, 225, False)
    draw_centered_text("W: Jump, D: Move Right, S: Crouch, A: Move Left", arial, (255, 255, 0), 40, 250, False)
    draw_centered_text("SPACEBAR: Attack", arial, (255, 255, 0), 40, 275, False)

    # detect mouse clicks
    if start_button.draw(screen):
        start_game = True
    if exit_button.draw(screen):
        pygame.quit()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    pygame.display.update()



# GAME LOOP
# -----------------------------------------------------------------------------------------

quit = False
level = 1
# Creating players and enemies
player = Player('adventurer', 200, 200, 100, 100, 100, False)
player_healthbar = HealthBar(SCREEN_WIDTH - 250, 40 , player.health, player.max_health)
# Adding enemies to the group
enemy_group = pygame.sprite.Group()
number_of_enemies = 10
for i in range(number_of_enemies):
    snake = Player('snake', random.randint(10, 10000), 600, 100, 100, 100, False)
    enemy_group.add(snake) 

while not quit:
    clock.tick(FPS)
    draw_bg()
    if game_over == 0:
        draw_text(str(len(enemy_group)), pygame.font.Font("Pokemon GB.ttf", 64), (255, 255, 0), SCREEN_WIDTH // 2 - 30, 20)
    elif game_over == 1:
        draw_text("Press the victory button for the next level", pygame.font.Font("Pokemon GB.ttf", 16), (255, 255, 0), 75, 250)
    draw_text("Level " + str(level), pygame.font.Font("Pokemon GB.ttf", 32), (255, 200, 0), 10, 20)
    draw_text("Time Remaining:", pygame.font.Font("Pokemon GB.ttf", 20), (255, 200, 0), 10, 75)
    if seconds_left == 1:
        draw_text(str(seconds_left) + " second left", pygame.font.Font("Pokemon GB.ttf", 20), (255, 200, 0), 10, 100)
    else:
        draw_text(str(seconds_left) + " seconds left", pygame.font.Font("Pokemon GB.ttf", 20), (255, 200, 0), 10, 100)
    player_healthbar.draw(player.health)
    draw_text("Health: " + str(player.health), pygame.font.Font("Pokemon GB.ttf", 20), (255, 200, 0), SCREEN_WIDTH - 250, 10)

    # check if a second has passed to reduce seconds left
    if pygame.time.get_ticks() - timer > 1000 and game_over == 0:
        seconds_left -= 1
        timer = pygame.time.get_ticks()
    if seconds_left <= 0:
        game_over = -1
    


    # check if game is over
    if len(enemy_group) <= 0 and game_over == 0:
        game_over = 1
    if player.health <= 0:
        game_over = -1


    if game_over != 0:
        if game_over == 1:
            player.end_movement()
            if victory_button.draw(screen):
                level = level + 1
                timer = pygame.time.get_ticks()
                seconds_left = 30 * level * (1 - (level//10))
                player = Player('adventurer', 200, 200, 100, 100, 100, False)
                enemy_group = pygame.sprite.Group()
                number_of_enemies = number_of_enemies + 10
                for i in range(number_of_enemies):
                    snake = Player('snake', random.randint(10, 10000), 600, 100, 100, 100, False)
                    enemy_group.add(snake)
                game_over = 0
        if game_over == -1:
            player.end_movement()
            defeat_rect = defeat_img.get_rect()
            defeat_rect.centerx = SCREEN_WIDTH // 2
            defeat_rect.y = 10
            screen.blit(defeat_img, (defeat_rect.x, defeat_rect.y))
        if restart_button.draw(screen):
            timer = pygame.time.get_ticks()
            seconds_left = 30 * level * (1 - (level//10))
            screen_scroll = 0
            player = Player('adventurer', 200, 200, 100, 100, 100, False)
            enemy_group = pygame.sprite.Group()
            for i in range(number_of_enemies):
                snake = Player('snake', random.randint(10, 10000), 600, 100, 100, 100, False)
                enemy_group.add(snake)
            game_over = 0

    player.update()
    screen_scroll = player.move()
    bg_scroll -= screen_scroll
    player.draw()

    for enemy in enemy_group:
        enemy.update()
        enemy.enemy_move()
        enemy.draw()

    # Event Handling
    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            quit = True
        # Player action
        if game_over == 0:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    player.moving_right = True
                    player.moving_left = False
                    player.direction = 1
                    player.flipped = False
                    player.update_action(2) # Run
                if event.key == pygame.K_a:
                    player.moving_left = True
                    player.moving_right = False
                    player.direction = -1
                    player.flipped = True
                    player.update_action(2) # Run
                if event.key == pygame.K_w:
                    player.jump = True
                    player.update_action(4) # Jump
                if event.key == pygame.K_s and not player.in_air:
                    if player.moving_left or player.moving_right:
                        player.sliding = True
                        player.update_action(6) # Slide
                    else:
                        player.update_action(3) # Crouch
                if event.key == pygame.K_SPACE:
                    player.update_action(1) # Attack
                    player.attacking = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    player.moving_right = False
                    player.moving_left = False
                    player.update_action(0) # Idle
                if event.key == pygame.K_a:
                    player.moving_right = False
                    player.moving_left = False
                    player.update_action(0) # Idle
                if event.key == pygame.K_s:
                    if player.sliding:
                        player.update_action(2)
                        player.sliding = False
                    else:
                        player.update_action(0)
                if event.key == pygame.K_SPACE:
                    player.update_action(0) # Idle
                    player.moving_right = False
                    player.moving_left = False
                    player.attacking = False

    pygame.display.update()


pygame.quit()





