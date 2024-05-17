import os
import pygame

from settings import HITBOX_OFFSET, consumable_data, magic_data, weapon_data
from support import import_ini_file, modify_stats_file, import_folder
from ids import item_name, weapon_backend_name, item_quantity_location
from entity import Entity


class Player(Entity):
    def __init__(self, position, groups, obstacle_sprites, create_consume, destroy_consume, create_attack,
                 destroy_attack, create_magic, create_arrow, set_alert, get_near_drop, near_chest, teleport, db,
                 panel_group):
        super().__init__(groups)
        print("Creating player - player.py ~ 23")

        self.image = pygame.image.load('../graphics/player/down/down_0.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

        self.db = db
        self.save_slot = self.db.get_database()
        self.teleport = teleport
        self.panel_group = panel_group

        # graphic setup
        self.import_player_assets()
        self.status = 'down'

        # movement - ?
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        # dashing
        self.dashing = False
        self.dash_cooldown = 300
        self.dash_time = None

        self.obstacle_sprites = obstacle_sprites

        # consume timer
        self.consuming = False
        self.consume_cooldown = 400
        self.consume_time = None

        # consumable
        self.create_consume = create_consume
        self.destroy_consume = destroy_consume
        self.consume_index = 0
        self.update_consume_index = False
        self.update_cons_items = False
        self.consume = list(consumable_data.keys())[self.consume_index]
        self.can_switch_consume = True
        self.consume_switch_time = None
        self.consume_duration_cooldown = 200

        # weapon
        self.set_weapons()
        self.update_weapon_index = False

        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.can_switch_right_hand = True
        self.can_switch_left_hand = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        self.current_hand = 'right'

        # armor
        self.set_armor()

        # magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic_hand = self.set_magic_hand()
        self.magic = list(self.magic_hand.keys())[self.magic_index]
        # self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        self.create_arrow = create_arrow

        # stats
        self.stats = self.set_stats()
        self.max_stats = {'vitality': 1900, 'attunement': 99, 'endurance': 99, 'strength': 99, 'dexterity': 99,
                          'inteligence': 99, 'speed': 5}
        # self.upgrade_cost = {'health': 100, 'attack': 100, 'stamina': 100, 'magic': 100, 'speed': 100}
        # energy is not needed but include it if necessary
        # self.level = import_ini_file('../saves/plyr/lvl.ini', 0)["level"]
        self.level = int(self.db.get("FROM player WHERE stat?==?level")[0][2])

        # self.vitality = 400 + (self.stats['vitality'] * 15)
        # f = open("../saves/plyr/current_hp.ini", "r")
        # vit = f.read()
        # f.close()
        vit = int(self.db.get("FROM player WHERE stat?==?currenthp")[0][2])
        if int(vit) == 0:
            self.vitality = 400 + (self.stats['vitality'] * 15)
        else:
            self.vitality = int(vit)

        self.attunement = self.stats['attunement']
        self.magic_slots = self.define_magic_slots(self.attunement)
        self.endurance = self.stamina_calc()
        self.strength = self.stats['strength']
        self.dexterity = self.stats['dexterity']
        self.inteligence = self.stats['inteligence']
        self.speed = 6

        self.humanity = int(self.db.get("FROM player WHERE stat?==?humanity")[0][2])
        self.souls = int(self.db.get("FROM player WHERE stat?==?souls")[0][2])

        self.human_import = self.db.get("FROM player WHERE stat?==?ishuman")[0][2]
        self.human = self.str2bool(self.human_import)

        self.name = self.db.get("FROM player WHERE stat?==?name")[0][2]

        # getting the player's items from file
        self.consumable_inventory = self.db.get("FROM consumable_inv WHERE isequiped?==?1")
        self.magic_inventory = self.get_magic_uses(0)
        self.magic_inventory_inventory = self.set_magic_inventory()

        # self.has_estus = self.consumable_inventory['potion']
        # self.has_humanity = self.consumable_inventory['humanity']
        self.active_consumable_quantity = 0
        self.active_magic_quantity = 0

        # item event
        self.estus_happened = False
        self.humanity_happened = False

        # damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # audio
        self.weapon_attack_sound = pygame.mixer.Sound('../audio/sword.wav')
        self.weapon_attack_sound.set_volume(0.05)

        self.death_sound = pygame.mixer.Sound('../audio/player_death/you_died.wav')
        self.death_sound.set_volume(0.05)

        # later
        self.map = ''
        self.update_ui = False
        self.movement_locked = False

        self.current_enemy = ''

        self.set_alert = set_alert
        self.near_drop = get_near_drop
        self.drop_dict_size = 0
        self.pick_up = False
        self.can_pickup = True
        self.selection_time = pygame.time.get_ticks()

        self.near_chest = near_chest
        self.chest_dict_size = 0
        self.open_chest = False

        self.can_action = True

    def set_weapons(self):
        self.weapon_inventory = self.db.get("FROM weapon_inv WHERE isequiped?==?1")
        self.right_hand_weapons = []
        self.left_hand_weapons = []
        self.set_hands(self.weapon_inventory)

        self.weapon_index = 0
        self.left_hand_index = 0
        self.weapon = weapon_backend_name[self.right_hand_weapons[self.weapon_index][1]]
        self.left_weapon = weapon_backend_name[self.left_hand_weapons[self.left_hand_index][1]]

    def set_armor(self):
        self.armor_inventory = self.db.get(f"FROM armor_inv WHERE isequiped?==?1")

    def set_drop_dict_size(self, value):
        self.drop_dict_size = value

    def set_chest_dict_size(self, value):
        self.chest_dict_size = value

    def get_coord(self):
        col = self.rect.centerx // 64
        row = self.rect.centery // 64
        return (col, row)

    def str2bool(self, v):
        return v in ("True")

    def refresh_magic_uses(self, index):
        return import_ini_file(f'dbs/{self.save_slot}/magic_hand.ini', index)

    def get_magic_uses(self, index):
        return import_ini_file(f'dbs/{self.save_slot}/magic_hand.ini', index)

    # ugly af, will figure it out
    def define_magic_slots(self, attunement):
        if attunement <= 9:
            return 0
        elif attunement == 10 or attunement == 11:
            return 1
        elif attunement == 12 or attunement == 13:
            return 2
        elif attunement == 14 or attunement == 15:
            return 3
        elif 16 <= attunement <= 18:
            return 4
        elif 19 <= attunement <= 22:
            return 5
        else:
            return 6

    def stamina_calc(self):
        if 80 + (2 * self.stats['endurance']) >= self.max_stats['endurance']:
            return 160
        else:
            return 80 + (2 * self.stats['endurance'])

    # stops the player when given True
    def stop_me(self, is_stopped):
        if is_stopped:
            self.movement_locked = True
            self.direction[0] = 0
            self.direction[1] = 0
            self.speed = 0
        else:
            self.speed = self.stats['speed']

    # get the stats from file
    def set_stats(self):
        return import_ini_file(f'dbs/{self.save_slot}/stats.ini', 0)

    def update_stats(self):
        self.level = int(self.db.get("FROM player WHERE stat?==?level")[0][2])
        self.vitality = 400 + (self.stats['vitality'] * 15)
        self.attunement = self.stats['attunement']
        self.magic_slots = self.define_magic_slots(self.attunement)
        self.endurance = self.stamina_calc()
        self.strength = self.stats['strength']
        self.dexterity = self.stats['dexterity']
        self.inteligence = self.stats['inteligence']

    # modifies the stats file
    def modify_stats(self, stat, amount):
        modify_stats_file(stat, amount)

    # initializes the right hand
    def set_hands(self, inventory):
        flag_left = False
        flag_right = False
        for i in inventory:
            if i[3] == str(0) or i[3] == str(1):
                flag_right = True
                self.right_hand_weapons.append(i)
            if i[3] == str(7) or i[3] == str(8):
                flag_left = True
                self.left_hand_weapons.append(i)

        if not flag_right:
            self.right_hand_weapons.append(['0', '0000', '0', '0', '0000'])
        if not flag_left:
            self.left_hand_weapons.append(['0', '0000', '0', '0', '0000'])

    # initializes the magic hand
    def set_magic_hand(self):
        index = 0
        filesize = os.path.getsize(f'dbs/{self.save_slot}/magic_hand.ini')
        if filesize > 0:
            return import_ini_file(f'dbs/{self.save_slot}/magic_hand.ini', index)
        else:
            return {"none": 1}

    def set_magic_inventory(self):
        index = 0
        filesize = os.path.getsize(f'dbs/{self.save_slot}/magic_inventory.ini')
        if filesize > 0:
            dict = import_ini_file(f'dbs/{self.save_slot}/magic_inventory.ini', index)
            new_dict = {}
            for item in dict.keys():
                if dict[item] > 0:
                    new_dict[item] = dict[item]
            if len(new_dict) < 1:
                new_dict.update({"none": 1})
            return new_dict
        else:
            return {"none": 1}

    # general
    def import_player_assets(self):
        character_path = '../graphics/player/'
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_consume': [], 'left_consume': [], 'up_consume': [], 'down_consume': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': [],
            'falling': [], 'dead': []
        }

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def set_current_map(self, map):
        self.map = map

    def save_last_bonfire_position(self):
        f = open(f'dbs/{self.save_slot}/player_position.ini', "w")
        f.write(str(self.map) + '\n')
        f.write(str(self.hitbox.center))
        f.close()

    def get_humanity(self):
        return self.humanity

    def set_position(self, pos):
        self.hitbox.center = pos

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.attacking and not self.consuming and not self.movement_locked:
            # movement input
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            if keys[pygame.K_LSHIFT] and self.endurance > 10:
                self.endurance -= 4
                self.dashing = True
                self.dash_time = pygame.time.get_ticks()
                self.move(self.speed * 2)

            if keys[pygame.K_q] and self.can_action and self.vitality > 0:
                # play sound later
                if self.drop_dict_size > 0 or self.chest_dict_size > 0:
                    if self.near_chest():
                        self.selection_time = pygame.time.get_ticks()
                        self.open_chest = True
                        self.can_action = False
                    elif self.near_drop():
                        self.selection_time = pygame.time.get_ticks()
                        self.pick_up = True
                        self.can_action = False

                self.selection_time = pygame.time.get_ticks()
                self.can_action = False
                self.teleport()

            if keys[pygame.K_k] and not self.attacking and self.endurance > 0:
                # shoot an arrow
                self.attacking = True
                self.endurance -= 13
                self.attack_time = pygame.time.get_ticks()
                self.create_arrow('basic', self.status, self.rect)

            # consume input
            if keys[pygame.K_e] and not self.consuming:
                if self.active_consumable_quantity > 0:
                    if item_name[self.consumable_inventory[self.consume_index][1]] == 'estus flask':
                        if self.vitality < 400 + self.stats['vitality'] * 15:
                            # events
                            self.consuming = True
                            self.update_ui = True
                            # actions
                            self.active_consumable_quantity -= 1
                            self.consumable_inventory[self.consume_index][item_quantity_location] = self.active_consumable_quantity

                            self.db.update(f"INTO consumable_inv UPDATE quantity WHERE itemid?==?{self.consumable_inventory[self.consume_index][1]} TO {self.active_consumable_quantity}")
                            self.create_consume(item_name[self.consumable_inventory[self.consume_index][1]])
                            self.consume_time = pygame.time.get_ticks()
                            return

                    else:
                        self.consume_handler(item_name[self.consumable_inventory[self.consume_index][1]], self.consumable_inventory[self.consume_index][1])

            # attack input
            if (keys[pygame.K_SPACE] if len(self.panel_group) < 1 else keys[pygame.K_b]) and not self.attacking and self.endurance > 0:
                self.current_hand = 'right'
                self.attacking = True
                self.endurance -= 13
                self.attack_time = pygame.time.get_ticks()
                # for future me make it like if self.weapon in MAGIC_WEAPON_LIST or MELEE_WEAPON_LIST
                if self.weapon == 'wand':
                    self.cast_magic(self.magic_index)
                elif self.weapon == 'bow':
                    self.create_arrow('basic')
                else:
                    self.create_attack(self.current_hand)
                    self.weapon_attack_sound.play()

            if keys[pygame.K_LCTRL] and not self.attacking and self.endurance > 0:
                if self.left_weapon == 'wand' or self.weapon == 'wand':
                    self.cast_magic(self.magic_index)
                else:
                    self.current_hand = 'left'
                    self.attacking = True
                    self.endurance -= 13
                    self.attack_time = pygame.time.get_ticks()
                    self.create_attack(self.current_hand)
                    self.weapon_attack_sound.play()

            # switch consumable
            if keys[pygame.K_f] and self.can_switch_consume:
                # cooldown stuff
                self.can_switch_consume = False
                self.consume_switch_time = pygame.time.get_ticks()

                if self.consume_index < len(self.consumable_inventory) - 1:
                    self.consume_index += 1
                else:
                    self.consume_index = 0

            if keys[pygame.K_v] and self.can_switch_right_hand:
                # cooldown stuff
                self.can_switch_right_hand = False
                self.weapon_switch_time = pygame.time.get_ticks()

                if self.weapon_index < len(self.right_hand_weapons) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0

                self.weapon = weapon_backend_name[self.right_hand_weapons[self.weapon_index][1]]

            if keys[pygame.K_c] and self.can_switch_left_hand:
                # cooldown stuff
                self.can_switch_left_hand = False
                self.weapon_switch_time = pygame.time.get_ticks()

                if self.left_hand_index < len(self.left_hand_weapons) - 1:
                    self.left_hand_index += 1
                else:
                    self.left_hand_index = 0

                self.left_weapon = weapon_backend_name[self.left_hand_weapons[self.left_hand_index][1]]

            ########## FIX LATER PROBABLY USELESS CALCULATIONS ####################
            if keys[pygame.K_r] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()

                usable_magic_list = []
                for magic, value in self.magic_hand.items():
                    if value > 0:
                        usable_magic_list.append(magic)
                    # if value < 1 and magic == 'flame':
                    #     usable_magic_list.append(magic)

                if self.magic_index < len(list(self.magic_hand)) - 1:
                    self.magic_index += 1
                else:
                    self.magic_index = 0

                # give the magic variable the magic_hand's index element
                self.magic = list(self.magic_hand)[self.magic_index]

    def consume_handler(self, item, item_id):
        if item == 'humanity' and self.humanity < 9:
            # events
            self.consuming = True
            self.consume_time = pygame.time.get_ticks()

            # inventory logic
            self.active_consumable_quantity -= 1
            self.consumable_inventory[self.consume_index][item_quantity_location] = self.active_consumable_quantity

            if self.active_consumable_quantity == 0:
                self.db.delete(f'FROM consumable_inv WHERE itemid?==?{item_id}')
                del self.consumable_inventory[self.consume_index]
                self.consume_index = len(self.consumable_inventory) - 1
            elif self.active_consumable_quantity > 0:
                self.db.update(f"INTO consumable_inv UPDATE quantity WHERE itemid?==?{item_id} TO {self.active_consumable_quantity}")

            # create the event
            self.create_consume(item)
            self.update_ui = True
        elif item != 'humanity':
            # events
            self.consuming = True
            self.consume_time = pygame.time.get_ticks()

            # inventory logic
            self.active_consumable_quantity -= 1
            self.consumable_inventory[self.consume_index][item_quantity_location] = self.active_consumable_quantity

            if self.active_consumable_quantity == 0:
                self.db.delete(f'FROM consumable_inv WHERE itemid?==?{item_id}')
            elif self.active_consumable_quantity > 0:
                self.db.update(
                    f"INTO consumable_inv UPDATE quantity WHERE itemid?==?{item_id} TO {self.active_consumable_quantity}")

            # create the event
            self.create_consume(item)
            self.update_ui = True

    def selection_cooldown(self):
        if not self.can_action:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 200:
                self.can_action = True

    def cast_magic(self, index):
        # I want to get what's in the magic_hand and cast that
        #                 |
        if list(self.magic_hand.keys())[index] == 'heal':
            curr_index = 'heal'
            if self.magic_inventory[curr_index] > 0:
                self.magic_inventory[curr_index] -= 1
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(self.magic_hand.keys())[index]
                strength = list(magic_data.values())[index]['strength'] + self.stats['inteligence']
                self.create_magic(style, strength)
        if list(self.magic_hand.keys())[index] == 'flame':
            curr_index = 'flame'
            if self.magic_inventory[curr_index] > 0:
                self.magic_inventory[curr_index] -= 1
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(self.magic_hand.keys())[index]
                strength = list(magic_data.values())[index]['strength'] + self.stats['inteligence']
                self.create_magic(style, strength)
        if list(self.magic_hand.keys())[index] == 'fart5':
            curr_index = 'fart5'
            if self.magic_inventory[curr_index] > 0:
                self.magic_inventory[curr_index] -= 1
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(self.magic_hand.keys())[index]
                strength = list(magic_data.values())[index]['strength'] + self.stats['inteligence']
                self.create_magic(style, strength)

        strin = str(self.magic_inventory).replace("'", '"')
        modify_stats_file(f'dbs/{self.save_slot}/magic_hand.ini', strin)

    def refresh_magic_index(self):
        self.magic_index = 0

    def animate(self):
        # set animation to the player's status
        if 'falling' in self.status:
            self.status = 'falling'
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.image.get_rect(center=self.hitbox.center)

        # flicker
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    # update methods
    # wrong name ig
    def update_health(self):
        return self.stats['vitality']

    def update_active_consumable_quantity(self):
        if len(self.consumable_inventory) > 0:
            self.active_consumable_quantity = int(self.consumable_inventory[self.consume_index][item_quantity_location])

    def update_active_magic_quantity(self):
        self.active_magic_quantity = list(self.magic_inventory.values())[self.magic_index]

    def stamina_recovery(self):
        if self.endurance < 80 + (2 * self.stats['endurance']):
            self.endurance += 0.07
        else:
            self.endurance = 80 + (2 * self.stats['endurance'])

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        # actions
        if self.consuming:
            if current_time - self.consume_time >= self.consume_cooldown + consumable_data[self.consume]['cooldown']:
                self.consuming = False
                self.destroy_consume()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()

        if self.dashing:
            if current_time - self.dash_time >= self.dash_cooldown:
                self.dashing = False

        # switching items
        if not self.can_switch_consume:
            if current_time - self.consume_switch_time >= self.switch_duration_cooldown:
                self.can_switch_consume = True

        if not self.can_switch_right_hand:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_right_hand = True

        if not self.can_switch_left_hand:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_left_hand = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

        # damaging
        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    # getters
    def get_status(self):
        # idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status and not 'consume' in self.status:
                self.status = self.status + '_idle'

        if self.consuming:
            self.direction.x = 0
            self.direction.y = 0
            if not 'consume' in self.status:
                if 'idle' in self.status:
                    # override idle
                    self.status = self.status.replace('_idle', '_consume')
                else:
                    self.status = self.status + '_consume'
        else:
            if 'consume' in self.status:
                self.status = self.status.replace('_consume', '')

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    # override idle
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

        if self.vitality <= 0:
            self.status = 'dead'

    def player_alive(self, health):
        if health > 0:
            return True
        else:
            return False

    def get_position(self):
        return self.rect.center

    def get_active_consumable(self):
        return self.active_consumable_quantity

    def get_active_magic(self):
        return self.active_magic_quantity

    # damage getters
    def get_full_weapon_damage(self):
        base_damage = self.stats['strength']
        if self.current_hand == 'right':
            weapon_damage = weapon_data[self.weapon]['damage']
        else:
            weapon_damage = weapon_data[self.left_weapon]['damage']
        return base_damage + weapon_damage

    def get_full_magic_damage(self):
        base_damage = self.stats['inteligence']
        spell_damage = magic_data[self.magic]['strength']
        return base_damage + spell_damage

    def get_value_by_index(self, index):
        return list(self.stats.values())[index]

    def get_cost_by_index(self, index):
        return list(self.upgrade_cost.values())[index]

    def near_bonfire(self, object):
        player_vec = pygame.math.Vector2(self.rect.center)
        obj_vec = pygame.math.Vector2(object)
        return (player_vec - obj_vec).magnitude()

    # returns the distance and index of the teleport that is nearest to the player
    def nearest_object(self, objects):
        player_vec = pygame.math.Vector2(self.rect.center)
        ls = [(player_vec - pygame.math.Vector2(eval(vector))).magnitude() for vector in objects]
        # idk if its effective or not, but I trust python
        min_val = min(ls)
        min_index = ls.index(min_val)
        return min_val, min_index

    def update(self):
        self.input()
        self.cooldowns()
        self.selection_cooldown()
        self.get_status()
        self.animate()
        self.move(self.speed)
        self.update_health()
        self.get_active_consumable()
        self.get_active_magic()
        self.update_active_consumable_quantity()
        self.update_active_magic_quantity()
        self.stamina_recovery()
        self.player_alive(self.vitality)
