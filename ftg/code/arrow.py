import pygame


class Arrow(pygame.sprite.Sprite):
    def __init__(self, groups, player_status, start_rect, arrow_type, attackable, obstacle, a_group, damage_player, target_rect=""):
        super().__init__(groups)
        self.sprite_type = 'arrow'
        self.direction = player_status.split('_')[0]  # I want to get the 0.th item after the split
        self.speed = 4
        self.distance = 0
        self.start_rect = start_rect
        self.damage_player = damage_player
        self.target_rect = target_rect

        self.attackable_sprites = attackable
        self.obstacle_sprites = obstacle
        self.arrow_group = a_group

        # graphics
        full_path = f'../graphics/arrows/{arrow_type}/{self.direction}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        # doesn't work for some unknown reason
        path_to_bow = f'../graphics/weapons/bow/{self.direction}.PNG'
        self.bow_image = pygame.image.load(path_to_bow).convert_alpha()

        # audio
        self.bow_shot = pygame.mixer.Sound('../audio/attack/BowShot.wav')
        self.bow_shot.set_volume(0.4)
        self.bow_shot.play()

        # bow placement
        if self.direction == 'right':
            self.bow_rect = self.bow_image.get_rect(midleft=start_rect.midright + pygame.math.Vector2(0, 16))
        elif self.direction == 'left':
            self.bow_rect = self.bow_image.get_rect(midright=start_rect.midleft + pygame.math.Vector2(0, 16))
        elif self.direction == 'down':
            self.bow_rect = self.bow_image.get_rect(midtop=start_rect.midbottom + pygame.math.Vector2(-10, 0))
        else:
            self.bow_rect = self.bow_image.get_rect(midbottom=start_rect.midtop + pygame.math.Vector2(-10, 0))

        # arrow placement
        if self.direction == 'right':
            self.rect = self.image.get_rect(midleft=start_rect.midright + pygame.math.Vector2(0, 16))
        elif self.direction == 'left':
            self.rect = self.image.get_rect(midright=start_rect.midleft + pygame.math.Vector2(0, 16))
        elif self.direction == 'down':
            self.rect = self.image.get_rect(midtop=start_rect.midbottom + pygame.math.Vector2(-10, 0))
        else:
            self.rect = self.image.get_rect(midbottom=start_rect.midtop + pygame.math.Vector2(-10, 0))

    def update(self):
        if self.distance > 60:
            self.speed = 3

        if self.direction == 'right':
            self.rect.x += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed
        else:
            self.rect.y -= self.speed
        self.distance += 1

        if self.target_rect != "":
            if self.target_rect.colliderect(self.rect):
                self.damage_player('arrow', 300, 'leaf_attack')
                self.kill()

        if self.distance > 100:
            self.kill()

        # if the group meets with the other group it destroys the selected group elements that met
        pygame.sprite.groupcollide(self.arrow_group, self.obstacle_sprites, True, False)
        # keep it false for now
        pygame.sprite.groupcollide(self.arrow_group, self.attackable_sprites, False, False)


class TrapArrow(pygame.sprite.Sprite):
    def __init__(self, groups, player_rect, attackable, obstacle, a_group, direction, start_point, pressure_plate_rect, damage_player):
        super().__init__(groups)
        self.sprite_type = 'arrow'
        self.direction = direction
        self.speed = 7
        self.distance = 0
        self.start_point = start_point
        self.player_rect = player_rect
        self.damage_player = damage_player

        self.attackable_sprites = attackable
        self.obstacle_sprites = obstacle
        self.arrow_group = a_group

        # graphics
        full_path = '../graphics/arrows/basic/up.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        # audio
        self.bow_shot = pygame.mixer.Sound('../audio/attack/BowShot.wav')
        self.bow_shot.set_volume(0.4)
        self.bow_shot.play()

        # arrow placement from the pressure plate's position
        self.rect = self.image.get_rect(midtop=pressure_plate_rect.midbottom + pygame.math.Vector2(0, self.start_point))

    def update(self):
        if self.distance > 60:
            self.speed = 5

        if self.direction == 'down':
            self.rect.y -= self.speed

        self.distance += 1

        if self.distance > 100:
            self.kill()

        # if the group meets with the other group it destroys the selected group elements that met
        pygame.sprite.groupcollide(self.arrow_group, self.obstacle_sprites, True, False)
        # keep it false for now
        pygame.sprite.groupcollide(self.arrow_group, self.attackable_sprites, False, False)

        if self.player_rect.colliderect(self.rect):
            self.damage_player('arrow', 300, 'leaf_attack')
            self.kill()
