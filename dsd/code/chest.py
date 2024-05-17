import pygame

from support import import_folder


class Chest(pygame.sprite.Sprite):
    def __init__(self, pos, groups, status):
        super().__init__(groups)

        # graphic elements
        self.sprite_type = 'chest'

        # graphics setup
        self.frame_index = 0
        self.animation_speed = 0.15
        self.status = status
        self.import_graphics()
        self.image = self.animations[self.status][self.frame_index]

        # full_path = f'../graphics/drop/item/item.png'
        # self.image = pygame.image.load(full_path).convert_alpha()

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, -10)

        self.is_set = False

        # data
        self.health = 100

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 600

        self.loot = ''

    def set_loot(self, value):
        self.loot = value

    def get_loot(self):
        return self.loot

    def set_status(self, value):
        self.status = value

    def import_graphics(self):
        self.animations = {'closed': [], 'open': []}
        main_path = f'../graphics/chest/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        self.image.set_alpha(255)

    def get_player_distance_direction(self, player_rect_center):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player_rect_center)
        distance = (player_vec - enemy_vec).magnitude()  # convert vector into a distance

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()  # (0, 0) by default, if they are on the same spot we don't want to move it

        return (distance, direction)

    def get_damage(self, player_rect_center, get_full_weapon_damage, get_full_magic_damage, attack_type):
        if self.vulnerable:
            _, self.direction = self.get_player_distance_direction(player_rect_center)
            if attack_type == 'weapon':
                self.health -= get_full_weapon_damage()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def check_death(self):
        if self.health <= 0:
            self.kill()

    def update(self):
        self.animate()
        self.cooldowns()
        self.check_death()