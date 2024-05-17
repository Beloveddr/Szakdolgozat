import pygame

from settings import monster_data
from enemyEntity import EnemyEntity
from support import import_folder
from pathfinding.core.grid import Grid


class Enemy(EnemyEntity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles, add_souls, player_coord, player_rect):
        # general setup
        super().__init__(groups)
        self.sprite_type = 'enemy'

        # graphics setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-60, -60)
        self.obstacle_sprites = obstacle_sprites
        self.player_rect = player_rect

        self.matrix = []
        self.grid = Grid(matrix=self.matrix)
        self.pos = self.rect.center
        # path
        self.path = []
        self.collision_rects = []
        self.direction = pygame.math.Vector2(0, 0)
        self.player_coord = player_coord
        self.spawn_pos = self.get_coord()

        # stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.magic_damage = monster_info['magic_damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.magic_radius = monster_info['magic_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']
        self.magic_type = monster_info['magic_type']

        # player interaction
        # attack
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400

        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_souls = add_souls

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        # sounds
        self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
        self.attack_sound.set_volume(0.02)

        self.sounds = {
            'death_sound': pygame.mixer.Sound('../audio/death.wav'),
            'hit_sound': pygame.mixer.Sound('../audio/hit.wav')
        }

        for i in self.sounds:
            self.sounds[i].set_volume(0.02)

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'cast_magic': [], 'attack': []}
        main_path = f'../graphics/monsters/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_direction(self, player_rect_center):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player_rect_center)
        distance = (player_vec - enemy_vec).magnitude()  # convert vector into a distance

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()  # (0, 0) by default, if they are on the same spot we don't want to
            # move it

        return distance, direction

    def get_start_distance_direction(self, target):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(target[0])
        distance = (player_vec - enemy_vec).magnitude()  # convert vector into a distance

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()  # (0, 0) by default, if they are on the same spot we don't want to move it

        return (distance, direction)

    def get_monster_name(self):
        return self.monster_name

    def get_status(self, player_rect_center):
        distance, _ = self.get_player_distance_direction(player_rect_center)

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self):
        # enemy is attacking
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_type, self.attack_damage, self.attack_type)
            self.attack_sound.play()
        # enemy chilling
        elif self.status == 'move':
            self.create_path()
        elif self.status == 'idle' and self.get_coord() != self.spawn_pos:
            self.create_path(True)
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            if self.status == 'cast_magic':
                self.can_cast_magic = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            # flicker
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self, player_rect_center, full_weapon_damage, get_full_magic_damage, attack_type):
        if self.vulnerable:
            self.sounds['hit_sound'].play()
            _, self.direction = self.get_player_distance_direction(player_rect_center)
            if attack_type == 'weapon':
                self.health -= full_weapon_damage()
            else:
                # magic damage
                self.health -= get_full_magic_damage()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_souls(self.exp)
            self.sounds['death_sound'].play()

    def enemy_update(self, player_rect_center):
        self.get_status(player_rect_center)
        self.actions()

        # pathfinder
        self.pos += self.direction * self.speed
        self.check_collisions()
        self.rect.center = self.pos

        # raycast
        # print(self.cast_ray_to_player(self.obstacle_sprites, self.player_rect))

        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()


class BowEnemy(EnemyEntity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles, add_souls, player_coord, player_rect, create_arrow):
        # general setup
        super().__init__(groups)
        self.sprite_type = 'enemy'

        # graphics setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-60, -60)
        self.obstacle_sprites = obstacle_sprites
        self.player_rect = player_rect
        self.create_arrow = create_arrow

        self.matrix = []
        self.grid = Grid(matrix=self.matrix)
        self.pos = self.rect.center
        # path
        self.path = []
        self.collision_rects = []
        self.direction = pygame.math.Vector2(0, 0)
        self.player_coord = player_coord
        self.spawn_pos = self.get_coord()

        # stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.magic_damage = monster_info['magic_damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.magic_radius = monster_info['magic_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']
        self.magic_type = monster_info['magic_type']

        # player interaction
        # attack
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400

        self.can_shoot = True
        self.bow_time = None
        self.bow_cooldown = 2000

        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_souls = add_souls

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        # sounds
        self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
        self.attack_sound.set_volume(0.02)

        self.sounds = {
            'death_sound': pygame.mixer.Sound('../audio/death.wav'),
            'hit_sound': pygame.mixer.Sound('../audio/hit.wav')
        }

        for i in self.sounds:
            self.sounds[i].set_volume(0.02)

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'cast_magic': [], 'attack': [], 'shoot': []}
        main_path = f'../graphics/monsters/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_direction(self, player_rect_center):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player_rect_center)
        distance = (player_vec - enemy_vec).magnitude()  # convert vector into a distance

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()  # (0, 0) by default, if they are on the same spot we don't want to
            # move it

        return distance, direction

    def get_start_distance_direction(self, target):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(target[0])
        distance = (player_vec - enemy_vec).magnitude()  # convert vector into a distance

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()  # (0, 0) by default, if they are on the same spot we don't want to move it

        return (distance, direction)

    def get_monster_name(self):
        return self.monster_name

    def get_status(self, player_rect_center):
        distance, _ = self.get_player_distance_direction(player_rect_center)

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif 60 <= distance <= 300 and self.can_shoot:
            self.status = 'shoot'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self):
        # enemy is attacking
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_type, self.attack_damage, self.attack_type)
            self.attack_sound.play()
        elif self.status == 'shoot':
            if self.can_shoot:
                direction = ""
                x_diff = self.rect.centerx - self.player_rect.centerx
                y_diff = self.rect.centery - self.player_rect.centery
                if -200 >= x_diff or y_diff <= 200:
                    if x_diff >= y_diff:
                        if -200 <= x_diff <= 0:
                            direction = "down"
                        elif 0 <= x_diff <= 200:
                            direction = "left"
                    if x_diff <= y_diff:
                        if -200 <= y_diff <= 0:
                            direction = "right"
                        elif 0 <= y_diff <= 200:
                            direction = "up"

                    if direction != '':
                        self.create_arrow('basic', direction, self.rect, self.player_rect)

                self.bow_time = pygame.time.get_ticks()
                self.can_shoot = False

        # enemy chilling
        elif self.status == 'move':
            self.create_path()
        elif self.status == 'idle' and self.get_coord() != self.spawn_pos:
            self.create_path(True)
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            elif self.status == 'shoot':
                self.can_shoot = False

            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            # flicker
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.can_shoot:
            if current_time - self.bow_time >= self.bow_cooldown:
                self.can_shoot = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self, player_rect_center, get_full_weapon_damage, get_full_magic_damage, attack_type):
        if self.vulnerable:
            self.sounds['hit_sound'].play()
            _, self.direction = self.get_player_distance_direction(player_rect_center)
            if attack_type == 'weapon':
                self.health -= get_full_weapon_damage()
            else:
                # magic damage
                self.health -= get_full_magic_damage()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_souls(self.exp)
            self.sounds['death_sound'].play()

    def enemy_update(self, player_rect_center):
        self.get_status(player_rect_center)
        self.actions()

        # pathfinder
        self.pos += self.direction * self.speed
        self.check_collisions()
        self.rect.center = self.pos

        # raycast
        # print(self.cast_ray_to_player(self.obstacle_sprites, self.player_rect))

        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()
