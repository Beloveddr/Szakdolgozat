import pygame
from ids import *
from settings import *
from operator import itemgetter
from equip_menu import EquipMenu


class MenuInventory:
    def __init__(self, db, player):
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.db = db
        self.player = player
        self.slot = self.player.save_slot
        self.attribute_nr = len(player.stats)
        self.attribute_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # selection system
        self.selection_time = pygame.time.get_ticks()
        self.can_move = False
        self.selection_index = 0

        # the cursor's base position that indicates the buttons
        self.cursor_rect_x = 950
        self.cursor_rect_y = 110

        self.closed = False
        self.equip_menu_open = False

        self.empty_image = pygame.image.load('../graphics/blocks/empty/64x64transparent.png')

        self.item_graphics = []
        self.quantities = []
        self.get_item_images()

    # filling all the item positions (18) with empty or not empty element, it depends on the query !in order!
    def get_item_images(self):
        self.item_graphics = []
        self.quantities = []
        ls_weapon = self.db.get(f"FROM weapon_inv WHERE isequiped?==?1")
        ls_cons = self.db.get(f"FROM consumable_inv WHERE isequiped?==?1")
        ls_armor = self.db.get(f"FROM armor_inv WHERE isequiped?==?1")
        temp = ls_weapon + ls_cons
        temp.extend(ls_armor)
        for i in temp:
            i[3] = int(i[3])
        ls = sorted(temp, key=itemgetter(3))
        query_item_index = 0
        # not empty inventory
        if len(ls) > 0:
            for i in range(19):
                # print(query_item_index, 'item index')
                # print(ls[query_item_index], i, "ls i-th element")
                if i == ls[query_item_index][3]:
                    location = ls[query_item_index][1]
                    self.item_graphics.append(pygame.image.load(item_path[location]))
                    self.quantities.append(ls[query_item_index][item_quantity_location])
                    if query_item_index < len(ls) - 1:
                        query_item_index += 1
                else:
                    self.quantities.append(' ')
                    self.item_graphics.append(self.empty_image.copy())
        else:
            # empty inventory
            for i in range(19):
                self.quantities.append(' ')
                self.item_graphics.append(self.empty_image.copy())

    def get_closed(self):
        return self.closed

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_RIGHT] and self.selection_index < 18:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            elif keys[pygame.K_LEFT] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            elif keys[pygame.K_DOWN] and 0 <= self.selection_index < 18 and self.selection_index + 6 <= 18:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                if self.selection_index > 4:
                    self.selection_index += 6
                else:
                    self.selection_index += 7

            elif keys[pygame.K_UP] and self.selection_index > 6:
                if self.selection_index <= 10:
                    if self.selection_index == 5 or self.selection_index == 6:
                        self.selection_index -= 6
                    else:
                        self.selection_index -= 7
                else:
                    self.selection_index -= 6
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE] and not self.equip_menu_open:
                self.can_move = False
                self.player.update_ui = True
                self.player.update_consume_index = True
                self.selection_time = pygame.time.get_ticks()
                self.trigger(self.selection_index)

            # dequip
            if keys[pygame.K_q] and not self.equip_menu_open:
                self.player.update_ui = True
                self.player.update_consume_index = True
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.trigger(self.selection_index, True)

            if keys[pygame.K_BACKSPACE]:
                self.can_move = False
                self.player.update_ui = True
                self.selection_time = pygame.time.get_ticks()
                self.closed = True
                del self

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 170:
                self.can_move = True

    # trigger an event by index (values are made manually)
    def trigger(self, index, dequip=False):
        query_type = 'none'
        if index in [0, 1, 7, 8]:
            query_type = 'weapon'
        elif index in [2, 3, 4, 5, 6]:
            query_type = 'consumable'
        elif index in [13, 14, 15, 16]:
            query_type = 'armor'

        if dequip:
            self.db.update(f"INTO {query_type}_inv UPDATE isequiped WHERE slotindex?==?{index} TO 0")
            self.db.update(f"INTO {query_type}_inv UPDATE slotindex WHERE slotindex?==?{index} TO 19")
            self.get_item_images()
            self.can_move = False
            self.player.set_weapons()
            return

        self.can_move = False
        self.equip_menu_open = True
        self.equip_menu = EquipMenu(self.db, index, query_type)

    def text(self, text, x, y):
        # bg_rect = self.selection_box(WIDTH / 2 - (ITEM_BOX_SIZE / 2), HEIGTH / 2 + 70, True)
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def selection_box(self, x, y):
        bg_rect = pygame.Rect(x, y, STATUS_MENU_SIZE, STATUS_MENU_SIZE - 400)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def stat_box(self, x, y, width, height):
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def item_box(self, left, top, active):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_EQUIPMENT, ITEM_BOX_EQUIPMENT)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if active:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def item_box_small(self, left, top, active):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if active:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def item_overlay(self, x, y, item, button_index):
        active = False
        if self.selection_index == button_index:
            active = True
        bg_rect = self.item_box(x, y, active)  # weapon
        item_surf = item
        item_rect = item_surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(item_surf, item_rect)

    def item_overlay_small(self, x, y, item, button_index):
        active = False
        if self.selection_index == button_index:
            active = True
        bg_rect = self.item_box_small(x, y, active)  # weapon
        item_surf = item
        item_rect = item_surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(item_surf, item_rect)
        return bg_rect

    def display(self):
        window = self.selection_box(100, 10)
        self.stat_box(window.x + 810, 130, 280, 500)
        # weapons etc
        self.item_overlay(window.x + 100, window.y + 120, self.item_graphics[0], 0)
        self.item_overlay(window.x + 230, window.y + 120, self.item_graphics[1], 1)

        # consumable
        item = self.item_overlay_small(window.x + 360, window.y + 120, self.item_graphics[2], 2)
        self.text(self.quantities[2], item.x + 8, item.y + ITEM_BOX_SIZE + 9)
        item = self.item_overlay_small(window.x + 450, window.y + 120, self.item_graphics[3], 3)
        self.text(self.quantities[3], item.x + 8, item.y + ITEM_BOX_SIZE + 9)
        item = self.item_overlay_small(window.x + 540, window.y + 120, self.item_graphics[4], 4)
        self.text(self.quantities[4], item.x + 8, item.y + ITEM_BOX_SIZE + 9)
        item = self.item_overlay_small(window.x + 630, window.y + 120, self.item_graphics[5], 5)
        self.text(self.quantities[5], item.x + 8, item.y + ITEM_BOX_SIZE + 9)
        item = self.item_overlay_small(window.x + 720, window.y + 120, self.item_graphics[6], 6)
        self.text(self.quantities[6], item.x + 8, item.y + ITEM_BOX_SIZE + 9)

        self.item_overlay(window.x + 100, window.y + 250, self.item_graphics[7], 7)
        self.item_overlay(window.x + 230, window.y + 250, self.item_graphics[8], 8)

        # arrows / bolts
        item = self.item_overlay_small(window.x + 360, window.y + 250, self.item_graphics[9], 9)
        self.text(self.quantities[9], item.x + 8, item.y + ITEM_BOX_SIZE + 9)
        item = self.item_overlay_small(window.x + 450, window.y + 250, self.item_graphics[10], 10)
        self.text(self.quantities[10], item.x + 8, item.y + ITEM_BOX_SIZE + 9)
        item = self.item_overlay_small(window.x + 630, window.y + 250, self.item_graphics[11], 11)
        self.text(self.quantities[11], item.x + 8, item.y + ITEM_BOX_SIZE + 9)
        item = self.item_overlay_small(window.x + 720, window.y + 250, self.item_graphics[12], 12)
        self.text(self.quantities[12], item.x + 8, item.y + ITEM_BOX_SIZE + 9)

        # armor
        self.item_overlay(window.x + 100, window.y + 380, self.item_graphics[13], 13)
        self.item_overlay(window.x + 230, window.y + 380, self.item_graphics[14], 14)
        self.item_overlay(window.x + 360, window.y + 380, self.item_graphics[15], 15)
        self.item_overlay(window.x + 490, window.y + 380, self.item_graphics[16], 16)

        # rings
        self.item_overlay_small(window.x + 630, window.y + 400, self.item_graphics[17], 17)
        self.item_overlay_small(window.x + 720, window.y + 400, self.item_graphics[18], 18)

        if self.equip_menu_open:
            self.can_move = False
            self.equip_menu.display()
            if self.equip_menu.closed:
                self.player.update_ui = True
                self.player.update_consume_index = True
                self.player.update_weapon_index = True
                self.player.set_armor()
                self.get_item_images()
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.equip_menu_open = False
        else:
            self.input()
            self.selection_cooldown()
