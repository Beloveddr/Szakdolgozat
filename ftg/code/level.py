import random

import pygame.mixer

from support import *
from settings import UI_FONT, UI_FONT_SIZE, TILESIZE, ground_object_ids, weapon_data, consumable_data, stuck_doors, monster_loot_data, locked_doors, opener_ids, unlocker_doors, locations_db, TEXT_COLOR, WIDTH, HEIGTH, UI_BG_COLOR, UI_BORDER_COLOR, ENTITY_UPDATE_DISTANCE
from tile import Tile
from player import Player
from drop import Drop
from lost_souls import Lost_souls
from random import randint
from consumable import Consumable
from weapon import Weapon
from arrow import Arrow, TrapArrow
from bossWeapon import BossWeapon
from ui import UI
from enemy import Enemy, BowEnemy
from wizardEnemy import wizardEnemy
from npc import NPC
from boss import BossEnemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade
from igmenu import IgMenu
from popup import Popup, PopupText
from bonfire_menu import BonfireMenu
from chest import Chest
from pressure_plate import PressurePlate
from hidden_block import HiddenBlock
from hole import Hole
from ids import item_name, item_quantity_location


class Level:
    def __init__(self, db, teleported=False, player=None):
        print("Creating level - level.py ~ 28")
        self.save_slot = db.get_database()
        # get the display surface
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False
        self.in_game_menu_open = False
        self.alert = False
        self.db = db
        # self.main_menu_pause = True

        # font
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # sprite group setup
        self.visible_sprites = YSortCameraGroup(self.db.get_database(), teleported, self.get_last_bonfire_position()[0], self.get_map())
        self.obstacle_sprites = pygame.sprite.Group()

        # consume sprites
        self.current_consume = None
        self.consume_sprites = pygame.sprite.Group()
        self.consumable_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None

        self.current_boss_attack = None

        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        self.arrow_group = pygame.sprite.Group()
        self.pressure_plate_group = pygame.sprite.Group()

        # drop sprite
        self.drop = None
        self.drop_sprite = pygame.sprite.Group()

        self.lost_souls = None
        self.lost_souls_sprite = pygame.sprite.Group()

        # storing the teleport ids and positions here
        self.teleport_positions, self.drop_positions, self.drop_cont, self.chest_positions = {}, {}, {}, {}
        self.bonfire_position = (0, 0)

        self.drop_id, self.ground_items_id, self.chest_id = 0, 0, 0
        self.drop_obj_group, self.chest_object_group, self.hidden_block_group, self.panel_group = [], [], [], []

        # sprite setup
        map_split = self.get_map().split('-')
        self.map = map_split[0] if teleported else self.get_last_bonfire_position()[0]
        self.map_index = map_split[1]
        self.matrix, self.entity_group = [], []
        self.create_map(self.map, teleported, player)
        # print(self.matrix)

        self.closed_chest_exist = self.sort_out_open_chests(self.chest_positions)

        # matrix is ready after create_map(), so we make the grid obj
        # print(self.matrix)
        # self.grid = Grid(matrix=self.matrix)

        # user interface
        self.ui = UI(self.db, self.player)
        self.upgrade = Upgrade(self.db, self.player)
        self.ingamemenu = IgMenu(self.db, self.player, self.create_consume)
        self.popup = Popup(self.player, 'sword', 0)
        self.bonfire_menu = None

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        # helps knowing what type of enemy we are attacking
        self.current_enemy = ''

        # map elements
        self.objects = ''
        self.bonf_pos = (0, 0)

        # player events
        self.player_died = False
        # self.player_got_item = False

        self.play_one_time = True
        self.play_death_one_time = True
        # print(self.teleport_positions, "teleport positions level.py constructor")

        self.closed = False

        self.init_sound()

    def init_sound(self):
        self.bonfire_sound = pygame.mixer.Sound('../audio/event/bonfire.wav')
        self.bonfire_sound.set_volume(0.4)

    # setting up the world
    def create_map(self, map, teleported, player):
        self.objects = self.map
        id = 0

        layouts = {
            'boundary': import_csv_layout('../map/' + map + '/map_FloorBlocks.csv'),
            # 'boundary': import_csv_layout('../map/idk_map_boundary.csv'),
            # 'grass': import_csv_layout('../map/' + map + '/map_Grass.csv'),
            # 'floor': import_csv_layout('../map/idk_map_grass.csv'),
            # 'object': import_csv_layout('../map/idk_map_obj.csv'),
            'entities': import_csv_layout('../map/' + map + '/map_Entities.csv'),
            'object': import_csv_layout('../map/' + map + '/map_Objects.csv'),
            # 'entities': import_csv_layout('../map/idk_map_entities.csv'),
        }
        # graphics = {
        #     'grass': import_folder('../graphics/Grass'),
        #     'objects': import_folder('../graphics/' + self.objects + '_objects'),
        #     'floor': import_folder('../graphics/floor')
        # }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                matrix_row = []
                for col_index, col in enumerate(row):
                    if col != '-1':
                        if style == 'boundary':
                            matrix_row.append(0)
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'invisible')
                        # if map == 'map1':
                        #     if style == 'grass':
                        #         random_grass_image = choice(graphics['grass'])
                        #         Tile(
                        #             (x, y),
                        #             [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites],
                        #             'grass', random_grass_image
                        #         )
                        # if style == 'floor':
                        #     surff = graphics['floor'][0]
                        #     Tile((x, y), [self.visible_sprites], 'floor', surff)
                        # don't ask anything about in these
                        # if map == 'map1':
                        #     if style == 'object':
                        #         surf = graphics['objects'][int(col)]
                        #         Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'objects', surf)

                        if style == 'object':
                            if col == '252':
                                self.bonfire_position = (x + TILESIZE / 2, y + TILESIZE / 2)
                                # surf = graphics['objects'][1]
                                # bonfire_rect = surf.get_rect(midbottom=(x, y))
                                # print(surf.get_rect(midbottom=(x, y)))
                                # self.player.set_bonfire_position((x, y))
                                # Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'objects', surf)
                            elif col == '284':
                                # print("(" + str(x) + ", " + str(y) + ") teleport postition - level.py ~ 147")
                                self.teleport_positions[id] = "(" + str(x+TILESIZE/2) + ", " + str(y+TILESIZE/2) + ")"
                                id += 1
                                # we don't even need a tile for this
                                # surf = graphics['objects'][2]
                                # Tile((x, y), [self.visible_sprites], 'objects', surf)
                            # do we need an else?
                            # else:
                                # surf = graphics['objects'][0]
                                # print(surf.get_rect(midbottom=(x, y)))
                                # Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'objects', surf)
                            elif col == '499':
                                self.create_hidden_block((x + TILESIZE/2, y + TILESIZE/2))

                            elif col == '166':
                                Hole((x + TILESIZE/2, (y + TILESIZE/2) - 30), [self.visible_sprites, self.obstacle_sprites], self.player)

                        if style == 'entities':
                            is_boss = False
                            if col == '370':
                                # print("Create Solaire - level.py ~ 156")
                                npc_name = 'solaire'
                                npc = NPC(
                                    npc_name, (x, y),
                                    [self.visible_sprites, self.attackable_sprites],
                                    self.obstacle_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_souls, self.player.get_coord, self.player.get_position,
                                    self.show_custom_popup, self.get_ig_menu_open, self.db, self.panel_group
                                )
                                self.entity_group.append(npc)

                            elif col == '121':
                                # self.drop = Drop((x, y), [self.visible_sprites], '{"Key to the abyss": 1}')
                                # self.drop_positions[self.drop_id] = "(" + str(x + TILESIZE / 2) + ", " + str(
                                #     y + TILESIZE / 2) + ")"
                                # self.drop_cont[self.drop_id] = self.drop.get_loot()
                                # self.drop_id += 1
                                # self.drop_obj_group.append(self.drop)
                                #
                                # self.drop = Drop((x + 100, y), [self.visible_sprites], '{"Key to my ass": 1}')
                                # self.drop_positions[self.drop_id] = "(" + str((x+100) + TILESIZE / 2) + ", " + str(
                                #     y + TILESIZE / 2) + ")"
                                # self.drop_cont[self.drop_id] = self.drop.get_loot()
                                # self.drop_id += 1
                                # self.drop_obj_group.append(self.drop)
                                self.ground_items((x + TILESIZE/2, y + TILESIZE/2))

                            elif col == '251':
                                self.chest_creation((x + TILESIZE/2, y + TILESIZE/2))

                            elif col == '376':
                                self.create_trap((x + TILESIZE/2, y + TILESIZE/2))

                            elif col == '394':
                                if not teleported:
                                    self.player = Player(
                                        (x, y),
                                        [self.visible_sprites], self.obstacle_sprites,
                                        self.create_consume, self.destroy_consume,
                                        self.create_attack, self.destroy_attack,
                                        self.create_magic, self.create_arrow, self.set_alert,
                                        self.near_drop, self.near_chest, self.teleport, self.db, self.panel_group
                                    )
                                if player is not None:
                                    self.player = player
                                    self.player.obstacle_sprites = self.obstacle_sprites
                                    self.visible_sprites.add(self.player)
                                    # self.player = Player(
                                    #     (x, y),
                                    #     [self.visible_sprites], self.obstacle_sprites,
                                    #     self.create_consume, self.destroy_consume,
                                    #     self.create_attack, self.destroy_attack,
                                    #     self.create_magic, self.create_arrow, self.set_alert,
                                    #     self.near_drop, self.near_chest, self.teleport, self.db, self.panel_group,
                                    #     player
                                    # )
                            else:
                                if col == '389':
                                    monster_name = 'undead'
                                elif col == '390':
                                    monster_name = 'bamboo'
                                elif col == '391':
                                    monster_name = 'spirit'
                                elif col == '392':
                                    is_boss = True
                                    monster_name = 'raccoon'
                                elif col == '393':
                                    monster_name = 'squid'
                                if not is_boss:
                                    if monster_name == 'squid':
                                        enemy = wizardEnemy(
                                            monster_name, (x, y),
                                            [self.visible_sprites, self.attackable_sprites],
                                            self.obstacle_sprites,
                                            self.damage_player,
                                            self.trigger_death_particles,
                                            self.add_souls, self.player.get_coord
                                        )
                                        self.entity_group.append(enemy)
                                    else:
                                        if monster_name == "undead":
                                            enemy = BowEnemy(
                                                monster_name, (x, y),
                                                [self.visible_sprites, self.attackable_sprites],
                                                self.obstacle_sprites,
                                                self.damage_player,
                                                self.trigger_death_particles,
                                                self.add_souls, self.player.get_coord, self.player.rect,
                                                self.create_arrow
                                            )
                                        else:
                                            enemy = Enemy(
                                                monster_name, (x, y),
                                                [self.visible_sprites, self.attackable_sprites],
                                                self.obstacle_sprites,
                                                self.damage_player,
                                                self.trigger_death_particles,
                                                self.add_souls, self.player.get_coord, self.player.rect
                                            )
                                        self.entity_group.append(enemy)
                                if is_boss:
                                    pass
                                    # print("Create boss  - level.py ~ 208")
                                    # self.boss = BossEnemy(
                                    #     monster_name, (x, y),
                                    #     [self.visible_sprites, self.attackable_sprites],
                                    #     self.obstacle_sprites,
                                    #     self.damage_player,
                                    #     self.trigger_death_particles,
                                    #     self.add_souls,
                                    #     self.create_boss_attack,
                                    #     self.destroy_boss_attack
                                    # )
                                    # self.enemy_group.append(self.boss)
                    else:
                        if style == 'boundary':
                            matrix_row.append(1)
                if style == 'boundary':
                    self.matrix.append(matrix_row)

        # print(self.matrix)
        # give the player obj the map
        self.player.set_current_map(map)

        # self.player.set_position(1550, 1800)
        if not teleported:
            self.player.set_position(eval(self.get_last_bonfire_position()[1]))
        else:
            # print(self.teleport_positions.get(int(self.map_index)))
            self.player.set_position(eval(self.teleport_positions.get(int(self.map_index))))

            # creates the lost souls obj if lost souls exists
        if len(self.get_lost_souls()) > 0:
            if self.get_lost_souls()[0] == self.map:
                # print(self.get_lost_souls()[1], "- level.py ~ 227")
                self.create_lost_souls(self.get_lost_souls()[1])

        # give all the pathfinder entities the matrix of the map
        for i in self.entity_group:
            i.set_matrix(self.matrix)

    def get_last_bonfire_position(self):
        return import_last_position_file(f'dbs/{self.save_slot}/player_position.ini')

    def set_alert(self, value):
        self.alert = value

    def sort_out_open_chests(self, chests):
        flag = 0
        for i in chests:
            if eval(chests[i])[0] != 10000 and eval(chests[i])[1] != 10000:
                flag = 1

        return True if flag > 0 else False

    def create_trap(self, pos):
        PressurePlate(pos, [self.visible_sprites], self.player.rect, 'active', self.create_trap_arrow)

    def create_trap_arrow(self, direction, start_point, pressure_plate_rect):
        TrapArrow([self.visible_sprites, self.attack_sprites], self.player.rect, self.attackable_sprites,
                  self.obstacle_sprites, self.arrow_group, direction, start_point, pressure_plate_rect, self.damage_player)

    def create_hidden_block(self, pos):
        block = HiddenBlock(pos, [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], 'hidden', self.hidden_block_group)
        self.hidden_block_group.append(block)

    def ground_items(self, pos):
        query = self.db.get(f"FROM ground_objects WHERE map?==?{self.map} AND groundid?==?{self.ground_items_id}")
        self.ground_items_id += 1
        # item wasn't picked up when it's 0
        if query[0][2] == '0':
            loot = '{"' + ground_object_ids[query[0][3]] + '": ' + query[0][4] + '}'
            self.create_drop(pos, loot, True)
        return

    def chest_creation(self, pos):
        query = self.db.get(f"FROM chests WHERE map?==?{self.map} AND groundid?==?{self.chest_id}")
        loot = '{"' + ground_object_ids[query[0][3]] + '": ' + query[0][4] + '}'
        self.create_chest(pos, loot, 'closed' if query[0][2] == '0' else 'open')

    def create_chest(self, pos, loot, status):
        self.chest = Chest(pos, [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], status)
        self.chest.set_loot(loot)
        if status == 'closed':
            self.chest_positions[self.chest_id] = "(" + str(pos[0]) + ", " + str(
                pos[1]) + ")"
        elif status == 'open':
            self.chest_positions[self.chest_id] = "(" + str(10000) + ", " + str(
                10000) + ")"
        self.chest_object_group.append(self.chest)
        self.chest_id += 1

    def item_pick_up_handler(self, loot, is_set):
        self.player.pick_up = False
        if loot == '00retr00':
            self.retrieve_souls()
            return

        loot = loot.replace("'", '"')
        loot = json.loads(loot)
        item_drop = ''

        for item in loot:
            # if the item was a pre set item and not a drop
            if is_set:
                if item in list(ground_object_ids.values()):
                    object_id = list(ground_object_ids.keys())[list(ground_object_ids.values()).index(item)]
                    self.db.update(f"INTO ground_objects UPDATE ispickedup WHERE itemid?==?{object_id} AND map?==?{self.map} TO 1")

            if item in weapon_data.keys():
                item_drop = 'weapon_type'
            elif item in consumable_data.keys():
                item_drop = 'consumable_type'

            if item_drop == 'weapon_type':
                item_code = list(item_name.keys())[list(item_name.values()).index(item)]
                quantity = 0
                weapons = self.db.get("FROM weapon_inv WHERE quantity?>=?0")
                # for i in weapons:
                #     if i[1] == item_code:
                #         quantity = int(i[6]) + 1
                #         self.db.update(f"INTO weapon_inv UPDATE quantity WHERE itemid?==?{item_code} TO {quantity}")
                # if quantity == 0:
                self.add_item_to_db(str(item_code), 'weapon_inv', 1)
                self.ui.update_weapon_inventory()

            elif item_drop == 'consumable_type':
                item_code = list(item_name.keys())[list(item_name.values()).index(item)]
                quantity = 0
                consumables = self.db.get(f"FROM consumable_inv WHERE quantity?>=?0")
                for i in consumables:
                    if i[1] == item_code:
                        quantity = int(i[item_quantity_location]) + 1
                        self.db.update(f"INTO consumable_inv UPDATE quantity WHERE itemid?==?{item_code} TO {quantity}")
                        self.player.update_cons_items = True
                        self.player.update_ui = True
                if quantity == 0:
                    self.add_item_to_db(str(item_code), 'consumable_inv', 1)

                self.ui.update_consumable_inventory()
            if 'Key' in str(item):
                self.key_handler(item)

            # popup window
            self.popup = Popup(self.player, item, loot[item])
            self.alert = True

    def add_item_to_db(self, item, doc, quantity):
        item_postfix = item[2] + item[3]
        custom_id = self.db.get_id(doc)
        if item[0] == "2":
            self.db.add(''.join(["20", item_postfix, ',0,19,none,', str(quantity), ',', str(int(custom_id)+1), " INTO ", doc]))
            # self.db.add(f"20{item_postfix},0,19,none,{quantity},{int(custom_id)+1} INTO {db}")
        elif item[0] == "1":
            self.db.add(''.join(["10", item_postfix, ',0,19,none,', str(quantity), ',60,1,regular,', str(int(custom_id)+1), " INTO ", doc]))
            # self.db.add(f"10{item_postfix},0,19,none,{quantity},60,1,regular,{int(custom_id)+1} INTO {db}")

    def key_handler(self, key):
        door = ''
        if key == 'Key to the abyss':
            door = 'map2-1'

        self.db.update(f"INTO doors UPDATE islocked WHERE doorid?==?{door} TO 0")

    # getting the last position of death and souls.
    def get_lost_souls(self):
        file_list = []
        with open(f'dbs/{self.db.get_database()}/lost_souls.ini', 'r') as f:
            content = f.read()
            file_list = content.split('\n')
        f.close()
        return file_list

    # deleting everything from the lost souls file
    def souls_retrieved(self):
        file = open(f'dbs/{self.db.get_database()}/lost_souls.ini', "r+")
        file.truncate(0)
        file.close()

    # when the player hits the lost_soul object
    def retrieve_souls(self):
        # popup for retrieve souls
        self.player.souls += int(self.get_lost_souls()[2])
        self.player.humanity += int(self.get_lost_souls()[3])

        # modify_ini_file('../saves/plyr/lvl.ini', "souls", self.player.souls)
        self.db.update(f"INTO player UPDATE value WHERE stat?==?souls TO {self.player.souls}")
        # modify_ini_file('../saves/plyr/lvl.ini', "humanity", self.player.humanity)
        self.db.update(f"INTO player UPDATE value WHERE stat?==?humanity TO {self.player.humanity}")

        self.souls_retrieved()

    # when the player dies, overwrite the lost_souls.ini file
    def create_lost_souls_by_death(self):
        self.play_one_time = False
        f = open(f"dbs/{self.db.get_database()}/lost_souls.ini", "w")
        f.write(str(self.map) + '\n')
        f.write(str(self.player.get_position()) + '\n')
        f.write(str(round(self.player.souls)) + '\n')
        f.write(str(self.player.humanity) + '\n')
        f.close()

    def create_consume(self, item, is_from_menu=False):
        self.current_consume = Consumable(self.player, [self.visible_sprites, self.consume_sprites], item)
        # heal = list(consumable_data.values())[self.player.consume_index]['heal']

        if item == "estus flask":
            self.heal_player(consumable_data["potion"]["heal"])
        elif item == "humanity":
            self.add_humanity()
            self.heal_player(10000)

        if is_from_menu:
            self.destroy_consume()
            self.player.update_ui = True
            self.in_game_menu_open = False

    def create_attack(self, hand):
        self.magic_player.magic_flame = False
        self.current_attack = Weapon(self.player, hand, [self.visible_sprites, self.attack_sprites])

    def create_arrow(self, type, entity_status, entity_rect, target_rect=""):
        self.current_arrow = Arrow([self.visible_sprites, self.attack_sprites], entity_status, entity_rect,
                                   type, self.attack_sprites, self.obstacle_sprites, self.arrow_group, self.damage_player, target_rect)
        self.arrow_group.add(self.current_arrow)

    def create_boss_attack(self):
        self.current_boss_attack = BossWeapon(self.boss, [self.visible_sprites, self.attack_sprites])

    def create_drop(self, pos, loot, is_set=False):
        # I dont get it but it needs a +1, but it's not a problem because we reorder the dicts
        self.drop_id += 1
        self.drop = Drop((pos[0], pos[1]), [self.visible_sprites], str(loot))
        if is_set:
            self.drop.set_isset(True)
        self.drop_positions[self.drop_id] = "(" + str(pos[0]) + ", " + str(
            pos[1]) + ")"
        self.drop_cont[self.drop_id] = self.drop.get_loot()
        self.drop_id += 1
        self.drop_obj_group.append(self.drop)
        self.drop_cont = self.reorder_dict(self.drop_cont)
        self.drop_positions = self.reorder_dict(self.drop_positions)

    def create_lost_souls(self, pos):
        self.lost_souls = Lost_souls(eval(pos), [self.visible_sprites])
        self.drop_positions[self.drop_id] = "(" + str(eval(pos)[0] + TILESIZE / 2) + ", " + str(
            eval(pos)[1] + TILESIZE / 2) + ")"
        self.drop_cont[self.drop_id] = '00retr00'
        self.drop_id += 1
        self.drop_obj_group.append(self.lost_souls)

    def create_magic(self, style, strength):
        # I think an update for the inventory will be needed here, if we get a new magic but will see
        # self.ui.update_magic_inventory()
        print(strength, "- create_magic() level.py ~ 293")
        if style == 'heal':
            self.magic_player.heal(self.player, strength, [self.visible_sprites])
        if style == 'flame':
            self.magic_player.magic_flame = True
            self.magic_player.flame(self.player, [self.visible_sprites, self.attack_sprites])
        if style == "fart5":
            self.magic_player.magic_flame = True
            self.magic_player.fireball(self.player, [self.visible_sprites, self.attack_sprites, self.obstacle_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def destroy_boss_attack(self):
        if self.current_boss_attack:
            self.current_boss_attack.kill()
        self.current_boss_attack = None

    def destroy_consume(self):
        if self.current_consume:
            self.current_consume.kill()
        self.current_consume = None

    # maybe a copy of player attack logic but against the player
    def boss_attack_logic(self):
        pass

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                # return all the collidable sprites
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 65)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player.rect.center, self.player.get_full_weapon_damage, self.player.get_full_magic_damage, attack_sprite.sprite_type)
                            if target_sprite.sprite_type == 'enemy':
                                self.set_current_enemy(target_sprite.get_monster_name())
                            if target_sprite.sprite_type == 'npc':
                                self.set_current_enemy(target_sprite.get_npc_name())

    def set_current_enemy(self, monster_name):
        self.player.current_enemy = monster_name
        self.current_enemy = monster_name

    def get_current_enemy(self):
        return self.current_enemy

    def get_player_current_enemy(self):
        return self.player.current_enemy

    def damage_player(self, type, amount, attack_type):
        if self.player.vulnerable and self.player.vitality > 0:
            for i in self.player.armor_inventory:
                amount -= int(i[6])
            if amount < 0:
                amount = 0
            self.player.vitality -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()

            # spawn particles
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

    def heal_player(self, amount):
        if self.player.vitality + amount > 400 + self.player.stats['vitality'] * 15:
            self.player.vitality = 400 + self.player.stats['vitality'] * 15
        else:
            self.player.vitality += amount

    def add_humanity(self):
        if self.player.humanity < 9:
            self.player.humanity += 1
            # modify_ini_file('../saves/plyr/lvl.ini', "humanity", self.player.humanity)
            self.db.update(f"INTO player UPDATE value WHERE stat?==?humanity TO {self.player.humanity}")

    def trigger_death_particles(self, pos, monster_name):
        self.animation_player.create_particles(monster_name, pos, [self.visible_sprites])
        if random.randint(1, 100) < 98:
            # print(self.define_loot(monster_name))
            self.create_drop(pos, self.define_loot(monster_name))

    def define_loot(self, monster_name):
        loot_dict = {}
        loot_type = random.choice(list(monster_loot_data[monster_name]))
        loot_quantity = monster_loot_data[monster_name][loot_type]
        loot_dict.update({loot_type: loot_quantity})
        return loot_dict

    def add_souls(self, amount):
        self.player.souls += amount
        self.db.update(f"INTO player UPDATE value WHERE stat?==?souls TO {self.player.souls}")

    def toggle_bonfire_menu(self):
        if self.player.near_bonfire(self.bonfire_position) < 130 and self.player.vitality > 0:
            self.bonfire_menu = BonfireMenu(self.db, self.player, self.ui)
            # close the ingame menu if the player opens the bonfire menu
            self.bonfire_menu.reset_uses()
            self.in_game_menu_open = False
            self.heal_player(2000)

            self.db.update(f"INTO player UPDATE value WHERE stat?==?currenthp TO {self.player.vitality}")
            self.db.update(f"INTO consumable_inv UPDATE quantity WHERE itemid?==?2002 TO 5")
            self.player.update_cons_items = True

            # play it only when we enter the bonfire
            if not self.game_paused:
                self.bonfire_sound.play()

            self.game_paused = not self.game_paused
            self.player.movement_locked = not self.player.movement_locked

            # setting the bonfire menu to default
            self.bonfire_menu.set_defult_settings()

            # refresh magic uses ######## later ########

            self.player.save_last_bonfire_position()

    # setting the in-game menu
    def toggle_ig_menu(self):
        self.in_game_menu_open = not self.in_game_menu_open
        if self.in_game_menu_open:
            self.panel_group.append('ingame_menu_panel')
        else:
            self.panel_group.remove('ingame_menu_panel')

    def get_ig_menu_open(self):
        return self.in_game_menu_open

    # teleportation and map loading
    def teleport(self):
        # print(self.player.near_usable_object(locations_data[curr_location]), "- level.py ~ 444")
        if self.player.nearest_object(list(self.teleport_positions.values()))[0] < 130 and self.player.vitality > 0:

            tp_id = self.player.nearest_object(list(self.teleport_positions.values()))[1]
            door = self.map + "-" + str(tp_id)

            if door in locked_doors:
                # get the door from db
                quer = self.db.get(f"FROM doors WHERE doorid?==?{door}")

                islocked = quer[0][2]
                first_time = quer[0][3]
                if islocked == '1':
                    message = 'This door is locked.'
                    if door in stuck_doors:
                        message = 'This door is stuck.'
                    self.popup = PopupText(self.player, message)
                    self.alert = True
                    return

                if first_time == '1':
                    key_name = opener_ids[quer[0][1]]
                    message = f'used {key_name}'
                    self.db.update(f"INTO doors UPDATE firsttime WHERE doorid?==?{door} TO 0")

                    self.popup = PopupText(self.player, message)
                    self.alert = True
                    return
            if door in unlocker_doors:
                self.db.update(f"INTO doors UPDATE islocked WHERE doorid?==?{unlocker_doors[door]} TO 0")
                self.db.update(f"INTO doors UPDATE firsttime WHERE doorid?==?{unlocker_doors[door]} TO 0")

            # saving the player's health after using teleport
            self.db.update(f"INTO player UPDATE value WHERE stat?==?currenthp TO {self.player.vitality}")

            # set map to other map and restart level
            self.load_new_map(self.player.nearest_object(list(self.teleport_positions.values()))[1])
            self.__init__(self.db, True, self.player)

    # teleport from map to map
    def load_new_map(self, teleport_index):
        location = locations_db.get(self.map + "-" + str(teleport_index))
        self.db.update(f"INTO player UPDATE value WHERE stat?==?playermap TO {location}")

    # gets the current map from player_map.ini
    def get_map(self):
        content = self.db.get(f"FROM player WHERE stat?==?playermap")[0][2]
        return content

    # popup windows to show if there is a near usable object
    def show_custom_popup(self, text):
        text_surf = self.font.render(text, False, TEXT_COLOR)
        x = (WIDTH / 2) - 23
        y = HEIGTH - 130
        text_rect = text_surf.get_rect(bottomright=(x, y))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    # returns if we are near a teleport or not
    def near_teleport(self):
        if self.player.nearest_object(list(self.teleport_positions.values()))[0] < 130:
            return True
        else:
            return False

    def near_drop(self):
        if len(self.drop_positions) > 0:
            if self.player.nearest_object(list(self.drop_positions.values()))[0] < 100:
                return True
            else:
                return False
        return False

    def near_chest(self):
        if len(self.chest_positions) > 0:
            if self.player.nearest_object(list(self.chest_positions.values()))[0] < 100:
                return True
            else:
                return False
        return False

    def show_bonfire_popup(self):
        text_surf = self.font.render('m: rest at bonfire', False, TEXT_COLOR)
        x = 700
        y = 660
        text_rect = text_surf.get_rect(bottomright=(x, y))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    # returns if the player is in 130px distance near a bonfire object
    def near_bonfire(self):
        if self.player.near_bonfire(self.bonfire_position) < 130:
            return True
        else:
            return False

    # outside function that listens to the the ESC button
    def ESC_actions(self):
        if self.player.vitality > 0:
            # destroys the bonfire menu
            self.game_paused = False
            self.player.movement_locked = False
            # opens the ingame menu
            self.toggle_ig_menu()
            # setting the index of the menu to 0
            self.ingamemenu.selection_index = 0
            # destroys the child menus of the  igmenu
            self.ingamemenu.status_open = False
            self.ingamemenu.inventory_open = False
            self.ingamemenu.equipment_open = False

    # function to draw death screen
    def draw(self, text, size, x, y):
        font = pygame.font.Font(UI_FONT, size)
        text_surf = font.render(text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect()
        text_rect.center = (x, y)
        self.display_surface.blit(text_surf, text_rect)

    def check_death(self):
        if self.player.vitality <= 0:
            if self.play_one_time:
                self.create_lost_souls_by_death()

                # modify_ini_file('../saves/plyr/lvl.ini', "souls", 0)
                self.db.update(f"INTO player UPDATE value WHERE stat?==?souls TO 0")
                # modify_ini_file('../saves/plyr/lvl.ini', "humanity", 0)
                self.db.update(f"INTO player UPDATE value WHERE stat?==?humanity TO 0")

                # self.player.kill()
                self.player.stop_me(True)
                self.player_died = True
                # change_one_line('../saves/plyr/is_human.ini', 'False')
                self.db.update(f"INTO player UPDATE value WHERE stat?==?ishuman TO False")

                self.ui.set_humanity_ui_color(UI_BG_COLOR)

                # it doesn't play for some reason
                # self.player.death_sound.play()

                # destroy these so they won't be on the screen after death
                self.destroy_attack()
                self.destroy_consume()

            # death screen
            self.draw('you died', 65, WIDTH / 2, HEIGTH / 2)
            self.draw('press q', 25, WIDTH / 2, (HEIGTH / 2) + 70)

    def play_death_sound(self):
        if self.player_died:
            self.player.death_sound.play()

    def reorder_dict(self, dict):
        new_dict = {}
        new_index = 0
        for i in dict:
            new_dict[new_index] = dict[i]
            new_index += 1
        return new_dict

    def pick_up_logic(self):
        # give it the closest item
        # get the index in the dict of the closest item
        index = self.player.nearest_object(list(self.drop_positions.values()))[1]

        self.item_pick_up_handler(self.drop_cont[index], self.drop_obj_group[index].get_isset())

        # remove the items from the list
        del self.drop_cont[index]
        del self.drop_positions[index]

        # destroy the drop object individually
        self.drop_obj_group[index].kill()
        # delete the object from the object group
        self.drop_obj_group.remove(self.drop_obj_group[index])
        # reorder the dicts from (for example) {0,2,3} to {0,1,2} and set the ID to the dict's size-1
        # so the dict's next element will be 3 and not 4, to handle overflow?
        self.drop_cont = self.reorder_dict(self.drop_cont)
        self.drop_positions = self.reorder_dict(self.drop_positions)
        self.drop_id = len(self.drop_positions) - 1
        if self.drop_id == -1:
            self.drop_id = 0

        self.player.set_drop_dict_size(len(self.drop_positions))

    def open_chest_logic(self):
        index = self.player.nearest_object(list(self.chest_positions.values()))[1]
        self.db.update(
            f"INTO chests UPDATE isopen WHERE groundid?==?{index} AND map?==?{self.map} TO 1"
        )

        self.create_drop(eval(self.chest_positions[index]), self.chest_object_group[index].get_loot())

        # del self.chest_positions[index]
        self.chest_positions[index] = "(" + str(10000 + TILESIZE / 2) + ", " + str(
            10000 + TILESIZE / 2) + ")"

        self.chest_object_group[index].set_status('open')

        # self.chest_object_group.remove(self.chest_object_group[index])

        self.chest_positions = self.reorder_dict(self.chest_positions)
        self.chest_id = len(self.chest_positions) - 1
        if self.chest_id == -1:
            self.chest_id = 0

        self.player.set_chest_dict_size(len(self.chest_positions))

        self.player.open_chest = False

    # update and draw the game
    def run(self):
        self.visible_sprites.custom_draw(self.player.rect)
        self.ui.display(self.player)
        if self.game_paused:
            # display bonfire menu
            if not self.bonfire_menu.get_closed():
                self.bonfire_menu.display()
                # display upgrade menu
                if self.bonfire_menu.lvlup_open:
                    self.upgrade.display()
            self.player.stop_me(True)

        if self.in_game_menu_open:
            self.ingamemenu.display()
            if self.ingamemenu.quit_game:
                self.closed = True
            self.game_running()

        else:
            # run the game
            self.game_running()
            self.play_death_sound()
            if self.alert:
                self.popup.display()

    def game_running(self):
        # self.troubleshooter(self.panel_group)
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player.rect.center)
        self.visible_sprites.npc_update(self.player)
        self.player_attack_logic()

        # its fcking stupid
        self.player.stop_me(False)

        self.arrow_group.update()
        if self.near_teleport() and not self.alert:
            self.show_custom_popup('q: teleport')
        if self.near_bonfire() and not self.game_paused and not self.alert:
            self.show_bonfire_popup()
        if len(self.drop_positions) > 0 and not self.alert and not self.game_paused:
            self.player.set_drop_dict_size(len(self.drop_positions))
            if self.near_drop():
                self.show_custom_popup('q: pick up')
                if self.player.pick_up:
                    self.pick_up_logic()

        if self.closed_chest_exist:
            if len(self.chest_positions) > 0 and not self.alert and not self.game_paused:
                self.player.set_chest_dict_size(len(self.chest_positions))
                if self.near_chest():
                    self.show_custom_popup('q: open')
                    if self.player.open_chest:
                        self.player.pick_up = False
                        # get id and set the chest's status to open
                        self.open_chest_logic()

    def troubleshooter(self, value):
        text = self.font.render(str(value), True, pygame.Color("RED"))
        self.display_surface.blit(text, (WIDTH - 1000, 50))


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self, slot, teleported, last_bonfire_pos, get_map):
        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()  # (0, 0) by default

        self.save_slot = slot
        self.map = get_map.split('-')[0] if teleported else last_bonfire_pos

        # creating the floor
        self.floor_surf = pygame.image.load(f'../graphics/tilemap/{self.map}.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player_rect):
        # getting the offset
        self.offset.x = player_rect.centerx - self.half_width
        self.offset.y = player_rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            if (pygame.math.Vector2(player_rect.center) - pygame.math.Vector2(sprite.rect.center)).magnitude() < ENTITY_UPDATE_DISTANCE:
                offset_position = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_position)

    def enemy_update(self, player_rect_center):
        enemy_sprites = [sprite for sprite in self.sprites() if
                         hasattr(sprite, 'sprite_type')
                         and sprite.sprite_type == 'enemy'
                         and ((pygame.math.Vector2(player_rect_center)
                               - pygame.math.Vector2(sprite.rect.center)).magnitude() < ENTITY_UPDATE_DISTANCE)]
        for enemy in enemy_sprites:
            enemy.enemy_update(player_rect_center)

    def npc_update(self, player):
        npc_sprites = [sprite for sprite in self.sprites() if
                       hasattr(sprite, 'sprite_type')
                       and sprite.sprite_type == 'npc'
                       and ((pygame.math.Vector2(player.rect.center)
                             - pygame.math.Vector2(sprite.rect.center)).magnitude() < ENTITY_UPDATE_DISTANCE)]
        for npc in npc_sprites:
            npc.npc_update(player.rect.center)
