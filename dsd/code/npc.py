import pygame

from settings import npc_data
from NPCentity import NPCEntity
from dialogue import DialogueMenu
from support import import_one_line, import_folder, change_one_line
from pathfinding.core.grid import Grid


def near_player(player_pos, self_center):
    player_vec = pygame.math.Vector2(player_pos)
    self_vec = pygame.math.Vector2(self_center)
    dist = (player_vec - self_vec).magnitude()
    if dist < 100:
        # will leave it like this for now
        return True
    return False


class NPC(NPCEntity):
    def __init__(self, npc_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles, add_souls,
                 player_coord, player_pos, popup, get_ig_menu_open, db, panel_group):
        # general setup
        super().__init__(groups)
        self.sprite_type = 'npc'
        self.npc_name = npc_name
        self.panel_group = panel_group

        self.db = db

        # graphics setup
        self.import_graphics(npc_name)
        self.status = 'idle'
        self.image = pygame.image.load('../graphics/npc/' + str(self.npc_name) + '/down.png')

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-50, -40)
        self.obstacle_sprites = obstacle_sprites

        self.matrix = []
        self.grid = Grid(matrix=self.matrix)
        self.pos = self.rect.center
        # path
        self.path = []
        self.collision_rects = []
        self.direction = pygame.math.Vector2(0, 0)
        self.player_coord = player_coord
        self.player_pos = player_pos
        self.popup = popup
        self.slot = self.db.get_database()
        self.get_ig_menu_open = get_ig_menu_open

        self.spawn_pos = self.get_coord()

        # stats
        self.friendly_import = import_one_line('../data/' + str(self.npc_name) + '.ini')
        self.friendly = self.str2bool(self.friendly_import)
        npc_info = npc_data[self.npc_name]
        self.health = npc_info['health']
        self.exp = npc_info['exp']
        self.speed = npc_info['speed']
        self.attack_damage = npc_info['damage']
        self.magic_damage = npc_info['magic_damage']
        self.resistance = npc_info['resistance']
        self.attack_radius = npc_info['attack_radius']
        self.magic_radius = npc_info['magic_radius']
        self.notice_radius = npc_info['notice_radius']
        self.attack_type = npc_info['attack_type']
        self.magic_type = npc_info['magic_type']

        # player interaction
        # attack
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400

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
        self.attack_sound = pygame.mixer.Sound(npc_info['attack_sound'])
        self.attack_sound.set_volume(0.02)

        self.sounds = {
            'death_sound': pygame.mixer.Sound('../audio/death.wav'),
            'hit_sound': pygame.mixer.Sound('../audio/hit.wav')
        }

        for i in self.sounds:
            self.sounds[i].set_volume(0.02)

        self.start_pos = pos

        # selection system
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True
        self.dialogue_open = False
        self.dialogue = False

    # convert the string we get from the file to boolean
    def str2bool(self, v):
        return v in ("True")

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
            direction = pygame.math.Vector2()  # (0, 0) by default, if they are on the same spot we don't want to move it

        return (distance, direction)

    def get_start_distance_direction(self, target):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(target[0])
        distance = (player_vec - enemy_vec).magnitude()  # convert vector into a distance

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()  # (0, 0) by default, if they are on the same spot we don't want to move it

        return (distance, direction)

    def get_npc_name(self):
        return self.npc_name

    def get_status(self, player_rect_center):
        distance = self.get_player_distance_direction(player_rect_center)[0]
        if not self.friendly:
            if distance <= self.attack_radius and self.can_attack:
                if self.status != 'attack':
                    self.frame_index = 0
                self.status = 'attack'
            elif distance <= self.notice_radius:
                self.status = 'move'
            else:
                self.status = 'idle'
        else:
            self.status = 'idle'

    # wizard enemy
    def get_wizard_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        if not self.friendly:
            if distance <= self.magic_radius:
                if self.can_cast_magic:
                    if self.status != 'cast_magic':
                        self.frame_index = 0
                    self.status = 'cast_magic'
            elif distance <= self.notice_radius:
                self.status = 'move'
            else:
                self.status = 'idle'
        else:
            self.status = 'idle'

    def actions(self):
        # enemy is attacking
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_type, self.attack_damage, self.attack_type)
            self.attack_sound.play()
        elif self.status == 'cast_magic':
            self.magic_time = pygame.time.get_ticks()
            self.damage_player(self.attack_type, self.magic_damage, self.attack_type)
            self.attack_sound.play()
            self.can_cast_magic = False
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

        if not self.can_cast_magic:
            if current_time - self.magic_time >= self.magic_cooldown:
                self.can_cast_magic = True
                print(self.can_cast_magic)

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self, player, attack_type, _):
        if self.vulnerable:
            self.sounds['hit_sound'].play()
            if player.current_enemy == self.npc_name:
                self.friendly = False
                change_one_line('../data/' + str(self.npc_name) + '.ini', str('False'))
            _, self.direction = self.get_player_distance_direction(player.rect.center)
            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()
            else:
                # magic damage
                self.health -= player.get_full_magic_damage()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.npc_name)
            self.add_souls(self.exp)
            self.sounds['death_sound'].play()

        # giving the player the items

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move and not self.get_ig_menu_open():
            if keys[pygame.K_q]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.trigger()
        elif self.can_move:
            if keys[pygame.K_ESCAPE] or keys[pygame.K_BACKSPACE]:
                if self.dialogue_open:
                    if self.dialogue.shopmenu_open:
                        self.dialogue.shopmenu_open = False
                    self.dialogue_open = False
                    del self.dialogue

    def trigger(self):
        self.dialogue_open = not self.dialogue_open
        if self.dialogue_open:
            self.panel_group.append('npc_dialogue_panel')
            self.dialogue = DialogueMenu(self.npc_name, self.db)
        else:
            self.panel_group.remove('npc_dialogue_panel')
            del self.dialogue

    def input_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 200:
                self.can_move = True

    def npc_update(self, player_rect_center):
        self.get_status(player_rect_center)
        self.actions()

        # pathfinder
        self.pos += self.direction * self.speed
        self.check_collisions()
        self.rect.center = self.pos

        if self.friendly:
            if near_player(self.player_pos(), self.rect.center):
                if not self.dialogue_open and not self.get_ig_menu_open():
                    self.popup('q: talk')
                self.input()
                self.input_cooldown()

                if self.dialogue_open and not self.dialogue.get_closed():
                    self.dialogue.display()
                    if self.dialogue.get_closed():
                        self.dialogue_open = False
            else:
                if 'npc_dialogue_panel' in self.panel_group:
                    self.panel_group.remove('npc_dialogue_panel')
                self.dialogue_open = False

        self.hit_reaction()
        self.move(self.speed)
        # self.animate()
        self.cooldowns()
        self.check_death()
