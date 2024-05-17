import pygame
from settings import TILESIZE, HITBOX_OFFSET
from random import randint


class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player
        self.sounds = {
            'heal': pygame.mixer.Sound('../audio/heal.wav'),
            'flame': pygame.mixer.Sound('../audio/Fire.wav')
        }

        self.magic_flame = False

        for i in self.sounds:
            self.sounds[i].set_volume(0.02)

    def heal(self, player, strength, groups):
        self.sounds['heal'].play()
        player.vitality += strength
        if player.vitality + strength > 400 + player.stats['vitality'] * 15:
            player.vitality = 400 + player.stats['vitality'] * 15
        self.animation_player.create_particles('aura', player.rect.center, groups)
        self.animation_player.create_particles('heal', player.rect.center + pygame.math.Vector2(0, -60), groups)

    # does not work
    def fireball(self, player, groups):
        image = pygame.image.load('../graphics/particles/fart5/fart5.png').convert_alpha()
        rect = image.get_rect(topleft=(0, 0))
        # getting the direction we are facing
        if player.status.split('_')[0] == 'right':
            direction = pygame.math.Vector2(1, 0)
        elif player.status.split('_')[0] == 'left':
            direction = pygame.math.Vector2(-1, 0)
        elif player.status.split('_')[0] == 'up':
            direction = pygame.math.Vector2(0, -1)
        else:
            direction = pygame.math.Vector2(0, 1)

        self.collision(direction)
        self.move(direction, 5, rect.inflate(-6, HITBOX_OFFSET['player']))

        for i in range(1, 5):
            if direction.x:  # horizontal
                offset_x = (direction.x * i) * TILESIZE
                x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                self.animation_player.create_particles('fart5', (x, y), groups)
            else:  # vertical
                offset_y = (direction.y * i) * TILESIZE
                x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                self.animation_player.create_particles('fart5', (x, y), groups)

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def move(self, direction, speed, hitbox):
        if direction.magnitude() != 0:
            direction = direction.normalize()

        hitbox.x += direction.x * speed
        self.collision('horizontal')
        hitbox.y += direction.y * speed
        self.collision('vertical')
        self.rect.center = hitbox.center

    def flame(self, player, groups):
        self.sounds['flame'].play()

        if player.status.split('_')[0] == 'right':
            direction = pygame.math.Vector2(1, 0)
        elif player.status.split('_')[0] == 'left':
            direction = pygame.math.Vector2(-1, 0)
        elif player.status.split('_')[0] == 'up':
            direction = pygame.math.Vector2(0, -1)
        else:
            direction = pygame.math.Vector2(0, 1)

        for i in range(1, 5):
            if direction.x:  # horizontal
                offset_x = (direction.x * i) * TILESIZE
                x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                self.animation_player.create_particles('flame', (x, y), groups)
            else:  # vertical
                offset_y = (direction.y * i) * TILESIZE
                x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                self.animation_player.create_particles('flame', (x, y), groups)

