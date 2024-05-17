import pygame
from settings import ITEM_BOX_EQUIPMENT, TEXT_COLOR, UI_FONT, UI_FONT_SIZE, STATUS_MENU_SIZE, UI_BG_COLOR, UI_BORDER_COLOR, UI_BORDER_COLOR_ACTIVE
from ids import *


class EquipMenu():
    def __init__(self, db, index, type):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.base_index = index
        self.db = db
        self.slot = self.db.get_database()
        self.type = type

        self.empty_image = pygame.image.load('../graphics/blocks/empty/64x64transparent.png')

        # query
        if type == 'weapon':
            self.query = self.db.get("FROM weapon_inv WHERE quantity?>=?1")
        elif type == 'consumable':
            self.query = self.db.get("FROM consumable_inv WHERE quantity?>=?0")
        elif type == 'armor':
            if index == 13:
                set_part = 'head'
            elif index == 14:
                set_part = 'body'
            elif index == 15:
                set_part = 'hand'
            else:
                set_part = 'legs'

            self.query = self.db.get(f"FROM armor_inv WHERE quantity?>=?0 AND type?==?{set_part}")
        else:
            self.query = []

        # selection system
        self.selection_time = pygame.time.get_ticks()
        self.can_move = False
        self.selection_index = 0

        self.closed = False

        self.button_id = 0
        self.start_index = 0
        self.index_list = [0, 1, 2, 3]

        self.item_graphics = []
        self.item_names = []
        self.step = len(self.item_graphics) - 1
        self.get_items(self.query)

    def get_items(self, ls):
        query_item_index = 0
        for item in ls:
            location = ls[query_item_index][1]
            item_name_location = ls[query_item_index][1]
            self.item_names.append(item_name[item_name_location])
            self.item_graphics.append(pygame.image.load(item_path[location]))
            query_item_index += 1

        if len(self.item_graphics) < 4:
            if len(self.item_graphics) == 1:
                self.index_list = [0]
            elif len(self.item_graphics) == 2:
                self.index_list = [0, 1]
            elif len(self.item_graphics) == 3:
                self.index_list = [0, 1, 2]
        else:
            self.index_list = [0, 1, 2, 3]

        self.step = len(self.item_graphics) - 1

    def button_interactive(self, text, x, y, button_id):
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        if button_id == self.selection_index:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, text_rect.inflate(17, 17), 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_DOWN] and self.selection_index < self.step:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

                if self.selection_index > self.index_list[-1]:
                    self.reorder_index_list(True)

            elif keys[pygame.K_UP] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

                if self.selection_index < self.index_list[0]:
                    self.reorder_index_list(False)
            elif keys[pygame.K_q]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                if len(self.query) > 0:
                    self.trigger(self.selection_index)
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_BACKSPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.closed = True
                del self

    def trigger(self, index):
        # update current item's isequiped variable to 0
        self.db.update(f"INTO {self.type}_inv UPDATE isequiped WHERE slotindex?==?{self.base_index} TO 0")
        # update the isequiped variable to 1 where the selected item's customid is equals to customid
        self.db.update(f"INTO {self.type}_inv UPDATE isequiped WHERE customid?==?{self.query[index][-1]} TO 1")
        # update the slotindex to 19 of the current item on the current slotindex
        self.db.update(f"INTO {self.type}_inv UPDATE slotindex WHERE slotindex?==?{self.base_index} TO 19")
        self.db.update(f"INTO {self.type}_inv UPDATE slotindex WHERE customid?==?{self.query[index][-1]} TO {self.base_index}")

        self.closed = True

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 170:
                self.can_move = True

    def text(self, text, x, y, unbordered=False):
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topleft=(x, y))
        if not unbordered:
            pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

        self.display_surface.blit(text_surf, text_rect)

    def selection_box(self, x, y):
        bg_rect = pygame.Rect(x, y, STATUS_MENU_SIZE - 300, STATUS_MENU_SIZE - 400)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def draw_border(self, x, y, width, height, is_active):
        rect = pygame.Rect(x, y, width, height)
        if is_active:
            color = UI_BORDER_COLOR_ACTIVE
        else:
            color = UI_BORDER_COLOR
        pygame.draw.rect(self.display_surface, color, rect, 3)

    def item_overlay(self, x, y, item, button_index):
        active = False
        if self.selection_index == button_index:
            active = True
        bg_rect = self.item_box(x, y, active)
        item_rect = item.get_rect(topleft=bg_rect.topleft)
        item_rect.x += 15
        item_rect.y += 32
        self.text(self.item_names[button_index], item_rect.x + 85, item_rect.y - 10)
        self.text(menu_item_descriptions[self.query[button_index][1]], item_rect.x + 85, item_rect.y + 30)
        # self.text('stats', item_rect.x + 600, item_rect.y + 30)

        self.display_surface.blit(item, item_rect)

        if self.type != "weapon" and self.type != "armor":
            self.text(self.query[button_index][item_quantity_location], item_rect.x + 40, item_rect.y + 40, True)

    def item_box(self, left, top, active):
        bg_rect = pygame.Rect(left, top, 720, ITEM_BOX_EQUIPMENT)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if active:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def reorder_index_list(self, index_is_bigger):
        if index_is_bigger:
            self.index_list = [index + 1 for index in self.index_list]
        else:
            self.index_list = [index - 1 for index in self.index_list]

    def display(self):
        self.selection_cooldown()
        self.input()
        self.selection_box(100, 10)

        if len(self.query) > 0:
            offset_y = 0
            for i in self.index_list:
                self.item_overlay(140, 100 + offset_y, self.item_graphics[i], i)
                offset_y += 122

        self.draw_border(100, 80, 800, 570, False)
