import pygame

from settings import WIDTH, HEIGTH, UI_FONT, UI_FONT_SIZE, UI_SMALLER_FONT_SIZE, UI_HUMANITY_ACTIVE_COLOR, magic_data, TEXT_COLOR, UI_BORDER_COLOR, UI_BG_COLOR, STATUS_MENU_SIZE, UI_BORDER_COLOR_ACTIVE, BONFIRE_MENU_LIST
from upgrade import Upgrade
from support import import_ini_file, modify_stats_file
from popup import PopupText


class BonfireMenu:
    def __init__(self, db, player, ui):
        # general setup
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.display_surface = pygame.display.get_surface()
        self.db = db
        self.player = player
        self.ui = ui
        self.slot = db.get_database()

        # child menus
        self.lvlup_menu, self.attune_menu = None, None

        self.lvlup_open, self.attune_menu_open = False, False

        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.font_small = pygame.font.Font(UI_FONT, UI_SMALLER_FONT_SIZE)

        # selection system
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True

        self.closed = False

        self.box_width, self.box_height, self.box_x, self.box_y = 330, 400, 120, 80

        # the cursor's base position that indicates the buttons
        self.cursor_rect_x = self.box_x + 22

        self.this_is_the_active_menu = True

        # attune box
        self.attune_box_x, self.attune_box_y = 100, 35

        self.small_border_x = self.attune_box_x + 40
        self.small_border_y = self.attune_box_y + 90

        self.button_id, self.attune_selection_index = 0, 0
        self.attribute_nr = player.magic_slots

        # equip inner method elements
        self.attune_inner_selection_index, self.input_active_slot, self.output_active_slot = 0, 0, 0
        self.inner_trigger_active = False

        self.update_magic_inventory()
        self.get_magic_from_inventory()
        self.none_image = pygame.image.load('../graphics/particles/none/64none.png')

        self.alert = False

    # doesn't work lol - REMOVE LATER PROBABLY - Sekiraw
    def reset_uses(self):
        input_dict = self.player.magic_hand
        hand = []
        for k in list(input_dict):
            hand.append(k)

        self.player.magic_hand = {}
        for k in hand:
            self.player.magic_hand[k] = magic_data[k]["uses"]

        strin = str(self.player.magic_hand).replace("'", '"')
        modify_stats_file(f'dbs/{self.slot}/magic_hand.ini', strin)

        self.player.update_ui = True

    def update_slots(self):
        self.attribute_nr = self.player.magic_slots

    def update_magic_inventory(self):
        self.magic_graphics = []

        output = {}
        # going through the magic_hand's keys and give the element that's bigger than 0
        for inv_item in self.player.magic_hand.keys():
            output[inv_item] = {"graphic": magic_data[inv_item]["graphic"]}

        for magic in output.values():
            magic = pygame.image.load(magic['graphic']).convert_alpha()
            self.magic_graphics.append(magic)

    def get_magic_from_inventory(self):
        self.magic_graphics_inv = []
        self.output = {}
        # storing the indexes and names of usable magic's
        self.new_indexes = {}
        i = 0
        # going through the magic_hand's keys and give the element that's bigger than 0
        for inv_item in self.player.magic_inventory_inventory.keys():
            self.output[inv_item] = {"graphic": magic_data[inv_item]["graphic"],
                                     "name": magic_data[inv_item]["name"],
                                     'type': magic_data[inv_item]["type"],
                                     'uses': magic_data[inv_item]["uses"],
                                     'int': magic_data[inv_item]["int"],
                                     'fth': magic_data[inv_item]["fth"],
                                     }
            self.new_indexes[i] = inv_item
            i += 1

        for magic in self.output.values():
            magic = pygame.image.load(magic['graphic']).convert_alpha()
            self.magic_graphics_inv.append(magic)

    def get_closed(self):
        return self.closed

    def set_defult_settings(self):
        self.lvlup_open = False
        self.attune_menu_open = False
        self.this_is_the_active_menu = True
        self.selection_index = 0

        self.button_id = 0
        self.attune_selection_index = 0

        # equip inner method elements
        self.attune_inner_selection_index = 0
        self.active_slot = 0
        self.inner_trigger_active = False

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if self.this_is_the_active_menu and not self.alert:
                if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.selection_index < 4:
                    self.selection_index += 1
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()

                elif (keys[pygame.K_UP] or keys[pygame.K_w]) and self.selection_index >= 1:
                    self.selection_index -= 1
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()

                if keys[pygame.K_SPACE]:
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()
                    self.trigger(self.selection_index)

            if keys[pygame.K_q]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.alert = False

            if keys[pygame.K_BACKSPACE]:
                self.alert = False
                self.lvlup_open = False
                self.attune_menu_open = False
                self.this_is_the_active_menu = True
                self.player.movement_locked = False

    def attune_input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if self.inner_trigger_active:
                if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.attune_inner_selection_index < len(
                        self.player.magic_inventory_inventory) - 1:
                    self.attune_inner_selection_index += 1
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()

                if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.attune_inner_selection_index >= 1:
                    self.attune_inner_selection_index -= 1
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()

                if keys[pygame.K_SPACE]:
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()
                    self.attune_magic_trigger(self.attune_inner_selection_index)

                if keys[pygame.K_BACKSPACE]:
                    self.inner_trigger_active = False
                    self.attune_inner_selection_index = 0

            else:
                if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.attune_selection_index < self.attribute_nr - 1:
                    self.attune_selection_index += 1
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()

                if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.attune_selection_index >= 1:
                    self.attune_selection_index -= 1
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()

                if keys[pygame.K_SPACE]:
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()
                    self.attune_trigger(self.attune_selection_index)

                if keys[pygame.K_BACKSPACE]:
                    self.attune_menu_open = False
                    self.attune_selection_index = 0
                    self.this_is_the_active_menu = True

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 150:
                self.can_move = True

    # trigger an event by index (values are made manually)
    def trigger(self, index):
        if index == 0:
            self.lvlup_open = True
        if index == 1:
            self.attune_menu_open = True
        if index == 4:
            if self.player.get_humanity() > 0:
                self.alert = True
                self.popup = PopupText(self.player, 'Humanity restored.')
                self.ui.set_humanity_ui_color(UI_HUMANITY_ACTIVE_COLOR)
                self.player.humanity -= 1
                self.player.human = True
                # change_one_line('../saves/plyr/is_human.ini', 'True')
                self.db.update(f"INTO player UPDATE value WHERE stat?==?ishuman TO True")
                self.db.update(f"INTO player UPDATE value WHERE stat?==?humanity TO {self.player.humanity}")

    def attune_trigger(self, index):
        self.input_active_slot = index
        self.inner_trigger_active = True

    # build in a converter and updater for the inventory
    def attune_magic_trigger(self, index):
        self.output_active_slot = index

        # swap magic
        self.swap_magic(self.input_active_slot, self.output_active_slot)

        self.inner_trigger_active = False
        self.attune_inner_selection_index = 0

    def swap_magic(self, input, output):
        in_dict = import_ini_file(f'dbs/{self.slot}/magic_inventory.ini', 0)
        output_dict = {}
        # getting the elements that are in inventory
        for key, value in in_dict.items():
            if value >= 1:
                output_dict[key] = value

        input_dict = import_ini_file(f'dbs/{self.slot}/magic_hand.ini', 0)
        if input >= len(self.player.magic_hand):
            if input != len(self.player.magic_hand):
                input = len(self.player.magic_hand)

        # delete the old key and replace it with the new one
        hand = []
        inventory = []
        for k in list(input_dict):
            hand.append(k)
        for k in list(output_dict):
            inventory.append(k)

        # handle if the input index is bigger then the size of current hand
        if input >= len(hand):
            hand.append("empty")
            input = hand.index("empty")

        hand[input] = inventory[output]
        self.player.magic_hand = {}
        for k in hand:
            self.player.magic_hand[k] = magic_data[k]["uses"]

        # make changes in the file and reload
        strin = str(self.player.magic_hand).replace("'", '"')
        modify_stats_file(f'dbs/{self.slot}/magic_hand.ini', strin)
        # updating the other functions
        self.player.magic_hand = self.player.set_magic_hand()
        self.player.magic_inventory = self.player.refresh_magic_uses(0)
        self.update_magic_inventory()
        # setting the index to 0 to evade crashes
        self.player.magic_index = 0
        self.player.update_active_magic_quantity()
        self.player.update_ui = True

    def draw_text(self, text, size, x, y):
        text_surface = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def button(self, text, x, y):
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def button_boarderless(self, text, x, y):
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topleft=(x, y))
        self.display_surface.blit(text_surf, text_rect)

    def sizeable_button(self, text, x, y):
        text_surf = self.font_small.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def box(self, x, y, width, height):
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def selection_box(self, x, y):
        bg_rect = pygame.Rect(x, y, STATUS_MENU_SIZE, STATUS_MENU_SIZE - 350)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def draw_border(self, x, y, width, height, is_active):
        rect = pygame.Rect(x, y, width, height)
        if is_active:
            color = UI_BORDER_COLOR_ACTIVE
        else:
            color = UI_BORDER_COLOR
        pygame.draw.rect(self.display_surface, color, rect, 3)

    def show_menu(self):
        bg_rect = self.selection_box(1000, 20)
        surf = pygame.image.load('../graphics/ingame_menu/igtop.png')
        rect = surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(surf, rect)

    def display(self):
        self.player.movement_locked = True
        if self.attune_menu_open:
            self.attune_input()
        else:
            self.input()
        self.box(self.box_x, self.box_y, self.box_width, self.box_height)
        times = 0
        for item in BONFIRE_MENU_LIST:
            self.button(item, self.box_x + 50, (self.box_y + 30) + times)
            times += 40

        # self.show_menu()
        self.selection_cooldown()
        if self.selection_index == 0:
            self.draw_text('*', 15, self.cursor_rect_x, self.box_y + 39)
        elif self.selection_index == 1:
            self.draw_text('*', 15, self.cursor_rect_x, self.box_y + 79)
        elif self.selection_index == 2:
            self.draw_text('*', 15, self.cursor_rect_x, self.box_y + 119)
        elif self.selection_index == 3:
            self.draw_text('*', 15, self.cursor_rect_x, self.box_y + 159)
        elif self.selection_index == 4:
            self.draw_text('*', 15, self.cursor_rect_x, self.box_y + 199)

        self.sizeable_button('select: up, down', self.box_x + 15, 420)
        self.sizeable_button('enter: space | exit: m', self.box_x + 15, 450)

        if self.lvlup_open:
            self.lvlup_menu = Upgrade(self.db, self.player)
            self.this_is_the_active_menu = False
            if self.lvlup_menu.get_closed():
                self.lvlup_open = False

        if self.attune_menu_open:
            self.update_slots()
            self.this_is_the_active_menu = False
            self.attune_menu_display()

        if self.alert:
            self.popup.display()

    # attune menu
    def button_interactive(self, text, x, y, button_id):
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        if button_id == self.attune_selection_index:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, text_rect.inflate(17, 17), 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def magic_overlay(self, x, y, magic_index, active_index):
        if magic_index >= len(self.magic_graphics) or self.magic_graphics[magic_index] == 'none':
            magic_surf = self.none_image
        else:
            magic_surf = self.magic_graphics[magic_index]
        magic_rect = magic_surf.get_rect(topleft=(x, y))

        if active_index == self.attune_selection_index:
            self.draw_border(x, y, magic_rect.width, magic_rect.height, True)
        else:
            self.draw_border(x, y, magic_rect.width, magic_rect.height, False)

        self.display_surface.blit(magic_surf, magic_rect)

    def magic_overlay_big(self, x, y, magic_index, active_index):
        if self.attune_inner_selection_index > self.r-1:
            magic_index += (self.attune_inner_selection_index - self.r) + 1
        if magic_index >= len(self.magic_graphics_inv) or self.magic_graphics_inv[magic_index] == 'none':
            magic_surf = self.none_image
        else:
            magic_surf = self.magic_graphics_inv[magic_index]
            self.button_boarderless(self.output[self.new_indexes[magic_index]]["name"], x + 70, y + 10)
            self.button_boarderless(self.output[self.new_indexes[magic_index]]["type"], x + (
                410 if self.output[self.new_indexes[magic_index]]["type"] == "pyromancy" else 437), y + 10)

        magic_rect = magic_surf.get_rect(topleft=(x, y))
        # troubleshoot "scrolling"
        # print(str(self.attune_inner_selection_index) + ' - select index')
        # print(str(active_index) + ' - active index')
        if active_index == self.attune_inner_selection_index:
            self.draw_border(x, y, magic_rect.width + 495, magic_rect.height, True)
        else:
            self.draw_border(x, y, magic_rect.width + 495, magic_rect.height, False)

        self.display_surface.blit(magic_surf, magic_rect)

    def attune_menu_display(self):
        self.selection_box(self.attune_box_x, self.attune_box_y)
        self.selection_cooldown()

        self.button('Attune magic', self.attune_box_x + 130, self.attune_box_y + 40)
        self.draw_border(self.small_border_x, self.small_border_y, 600, 100, False)
        offset_x = 0
        self.magic_id = 0
        for i in range(self.attribute_nr):
            self.magic_overlay((self.small_border_x + 20) + offset_x, self.small_border_y + 20, i, self.magic_id)
            offset_x += 70

            self.magic_id += 1

        self.draw_border(self.small_border_x, self.small_border_y + 130, 600, 320, False)
        offset_y = 0
        self.r = 4
        self.button_id = ((self.attune_inner_selection_index - self.r) + 1 if self.attune_inner_selection_index >= self.r else 0) if self.inner_trigger_active else 100
        for i in range(self.r):
            self.magic_overlay_big((self.small_border_x + 20), (self.small_border_y + 150) + offset_y,
                                   i, self.button_id)
            self.button_id += 1
            offset_y += 70

        self.button('select: up, down | enter: space | exit: backspace', 158, 620)
