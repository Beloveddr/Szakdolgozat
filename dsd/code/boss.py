import pygame

from settings import monster_data, BOSS_BAR_HEIGHT, BOSS_HEALTH_BAR_WIDTH, UI_FONT, boss_weapon_data, UI_FONT_SIZE, UI_BG_COLOR, UI_BORDER_COLOR, TEXT_COLOR, HEALTH_COLOR
from entity import Entity
from support import import_folder


class BossEnemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites,
                 damage_player, trigger_death_particles,
                 add_souls, create_boss_attack, destroy_boss_attack):
        # general setup
        super().__init__(groups)
        self.sprite_type = 'enemy'

        # graphics setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        # stats
        self.monster_name = monster_name
        self.monster_info = monster_data[self.monster_name]
        self.health = self.monster_info['health']
        self.exp = self.monster_info['exp']
        self.speed = self.monster_info['speed']
        self.attack_damage = self.monster_info['damage']
        self.magic_damage = self.monster_info['magic_damage']
        self.resistance = self.monster_info['resistance']
        self.attack_radius = self.monster_info['attack_radius']
        self.magic_radius = self.monster_info['magic_radius']
        self.notice_radius = self.monster_info['notice_radius']
        self.attack_type = self.monster_info['attack_type']
        self.magic_type = self.monster_info['magic_type']

        self.attack_type_boss = 'boss_weapon'

        # player interaction
        # attack
        self.create_attack = create_boss_attack
        self.destroy_attack = destroy_boss_attack

        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400
        self.attacking = False

        # magic
        self.can_cast_magic = True
        self.magic_time = None
        self.magic_cooldown = 2000

        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_souls = add_souls

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        # sounds
        self.attack_sound = pygame.mixer.Sound(self.monster_info['attack_sound'])
        self.attack_sound.set_volume(0.02)

        self.sounds = {
            'death_sound': pygame.mixer.Sound('../audio/death.wav'),
            'hit_sound': pygame.mixer.Sound('../audio/hit.wav')
        }

        for i in self.sounds:
            self.sounds[i].set_volume(0.02)

        # later docum
        self.health_bar_rect = pygame.Rect(380, 630, BOSS_HEALTH_BAR_WIDTH, BOSS_BAR_HEIGHT)
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        self.weapon = "sai"

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'cast_magic': [], 'attack': []}
        main_path = f'../graphics/monsters/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()  # convert vector into a distance

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()  # (0, 0) by default, if they are on the same spot we don't want to move it

        return (distance, direction)

    def get_monster_name(self):
        return self.monster_name

    def get_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius and self.can_attack:
            if not self.attacking:
                if self.status != 'attack':
                    self.frame_index = 0
                self.status = 'attack'
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
        elif distance <= self.notice_radius:
            # self.boss_fight()
            self.status = 'move'
        else:
            self.status = 'idle'

        # wizard enemy

    def get_wizard_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.magic_radius:
            if self.can_cast_magic:
                if self.status != 'cast_magic':
                    self.frame_index = 0
                self.status = 'cast_magic'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self, player):
        # enemy is attacking
        if self.status == 'attack':
            self.create_attack()
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_type, self.attack_damage, self.attack_type)
            self.attack_sound.play()
            self.can_attack = False
            self.attacking = True
        elif self.status == 'cast_magic':
            self.magic_time = pygame.time.get_ticks()
            self.damage_player(self.attack_type, self.magic_damage, self.attack_type)
            self.attack_sound.play()
            self.can_cast_magic = False
        # enemy chilling
        elif self.status == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

        if self.status == 'attack' or self.status == 'move':
            self.boss_fight()

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

        if not self.can_cast_magic:
            if current_time - self.magic_time >= self.magic_cooldown:
                self.can_cast_magic = True
                print(self.can_cast_magic)

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + boss_weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()

    def get_damage(self, player, attack_type):
        if attack_type != 'boss_weapon':
            if self.vulnerable:
                self.sounds['hit_sound'].play()
                self.direction = self.get_player_distance_direction(player)[1]
                if attack_type == 'weapon':
                    self.health -= player.get_full_weapon_damage()
                else:
                    self.health -= player.get_full_magic_damage()
                    # magic damage
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

    def show_bar(self, current, max_amount, bg_rect, color):
        # draw bg
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # converting stat to pixel
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # drawing the bar
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_boss_name(self):
        text_surf = self.font.render(str(self.monster_name), False, TEXT_COLOR)
        x = 485
        y = 620
        text_rect = text_surf.get_rect(bottomright=(x, y))

        # pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        # pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def boss_fight(self):
        self.show_boss_name()
        self.show_bar(self.health, self.monster_info['health'], self.health_bar_rect, HEALTH_COLOR)

    def update(self):
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()

    def enemy_update(self, player):
        if self.monster_name == 'squid':
            self.get_wizard_status(player)
        else:
            self.get_status(player)
        self.actions(player)
