import pygame
from settings import ITEM_BOX_EQUIPMENT, TEXT_COLOR, UI_FONT, UI_FONT_SIZE, STATUS_MENU_SIZE, UI_BG_COLOR, UI_BORDER_COLOR, UI_BORDER_COLOR_ACTIVE, WIDTH, HEIGTH
from ids import *


class MenuEquipment():
    def __init__(self, db, type, player, create_consume):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.db = db
        self.player = player
        self.type = type
        self.action_menu = None
        self.create_consume = create_consume

        # query
        self.query = self.db.get(f"FROM consumable_inv WHERE quantity?>=?0")

        # selection system
        self.selection_time = pygame.time.get_ticks()
        self.can_move = False
        self.selection_index = 0
        self.menu_selection_index = 0
        self.override_input = False

        self.closed = False

        self.button_id = 0
        self.start_index = 0
        self.index_list = [0, 1, 2, 3]

        self.item_graphics = []
        self.item_names = []
        self.step = len(self.item_graphics) - 1
        self.get_items(self.query)

        self.menu_images = []
        self.get_menu_images()

    def get_closed(self):
        return self.closed

    def get_menu_images(self):
        self.menu_images = [pygame.image.load(f"../graphics/ingame_menu/{counter}.png") for counter in range(7)]

    def get_items(self, ls):
        self.item_names = []
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

    def re_query(self, index, keep_index=False, delete_happened=False):
        type_list = ["consumable_inv", "none", "none", "none", "weapon_inv", "none", "armor_inv"]
        if not keep_index:
            if delete_happened:
                self.selection_index = self.selection_index - 1

        self.selection_index = 0
        self.item_graphics = []
        self.type = type_list[index]
        if type_list[index] != "none":
            self.query = self.db.get(f"FROM {type_list[index]} WHERE quantity?>=?0")
            self.get_items(self.query)
        else:
            self.index_list = [0]
        self.can_move = False
        self.selection_time = pygame.time.get_ticks()

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

        if self.can_move and not self.override_input:
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

            elif keys[pygame.K_LEFT] and self.menu_selection_index >= 1:
                self.menu_selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.re_query(self.menu_selection_index)

            elif keys[pygame.K_RIGHT] and self.menu_selection_index < 6:
                self.menu_selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.re_query(self.menu_selection_index)

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.trigger(self.selection_index)

            if keys[pygame.K_BACKSPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.closed = True
                del self

    def trigger(self, index):
        if (self.query[index][1] in non_useable_items) or (self.type == "weapon_inv" or self.type == "armor_inv"):
            # non usable and non droppable
            if self.query[index][2] == str(1):
                self.action_menu = ActionMenu(self.db, self.query[index], self.type, 3)
                return
            self.action_menu = ActionMenu(self.db, self.query[index], self.type, 1)
            return
        elif self.query[index][1] in non_droppable_items:
            self.action_menu = ActionMenu(self.db, self.query[index], self.type, 2, self.create_consume)
            return

        self.action_menu = ActionMenu(self.db, self.query[index], self.type, 0, self.create_consume)

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

        self.display_surface.blit(item, item_rect)

        if self.type != "weapon_inv" and self.type != "armor_inv":
            self.text(self.query[button_index][5], item_rect.x + 40, item_rect.y + 40, True)

    def menu_overlay(self, x, y, item, button_index):
        active = False
        if self.menu_selection_index == button_index:
            active = True
        bg_rect = self.menu_item_box(x, y, active)
        item_rect = item.get_rect(topleft=bg_rect.topleft)
        item_rect.x += 10
        item_rect.y += 10

        self.display_surface.blit(item, item_rect)

    def menu_item_box(self, left, top, active):
        bg_rect = pygame.Rect(left, top, 80, 80)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if active:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

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

        offset_x = 0
        for i in range(7):
            self.menu_overlay(140 + offset_x, 80, self.menu_images[i], i)
            offset_x += 90

        if len(self.item_graphics) > 0:
            offset_y = 0
            for i in self.index_list:
                self.item_overlay(140, 161 + offset_y, self.item_graphics[i], i)
                offset_y += 122

        self.draw_border(100, 80, 800, 570, False)

        if self.action_menu is not None:
            self.action_menu.display()
            self.override_input = True
            if self.action_menu.get_closed():
                if self.action_menu.changes_happened:
                    self.re_query(self.menu_selection_index, True, self.action_menu.delete_happened)
                    self.player.update_cons_items = True
                self.action_menu = None
                self.override_input = False
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()


class ActionMenu():
    def __init__(self, db, item, document, restriction, create_consume=None):
        self.db = db
        self.save_slot = self.db.get_database()
        self.item = item
        self.document = document
        self.item_type = self.document.split("_")[0]
        self.create_consume = create_consume

        # selection system
        self.can_move = False
        self.selection_time = pygame.time.get_ticks()
        self.selection_index = 0

        self.changes_happened = False
        self.delete_happened = False

        self.disable_use = False
        self.disable_drop = False
        self.just_quit = False
        if restriction == 1:
            self.disable_use = True
            self.selection_index = 1
        elif restriction == 2:
            self.disable_drop = True
        elif restriction == 3:
            self.disable_use = True
            self.disable_drop = True
            self.just_quit = True

        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        self.closed = False

    def get_closed(self):
        return self.closed

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 170:
                self.can_move = True

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_DOWN] and self.selection_index < (1 if not self.disable_drop else 0):
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            elif keys[pygame.K_UP] and self.selection_index >= (1 if not self.disable_use else 2):
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            elif keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.trigger(self.selection_index)

            if keys[pygame.K_BACKSPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.closed = True
                del self

    def trigger(self, index):
        if not self.just_quit:
            self.changes_happened = True
            if index == 0:
                if int(self.item[item_quantity_location]) > 0:
                    self.create_consume(item_name[self.item[1]], True)
                    self.inventory_handler(self.item)
            else:
                self.delete_happened = True
                self.db.delete(f"WHERE customid?==?{self.item[-1]} FROM {self.document}")

        self.closed = True
        del self

    def inventory_handler(self, item):
        custom_id = int(item[-1])
        quantity = int(item[5])
        # corner case for estus
        if item[1] == '2002':
            self.db.update(
                f"INTO {self.item_type}_inv UPDATE quantity WHERE customid?==?{custom_id} TO {quantity - 1}")
            return

        if quantity == 1:
            self.db.delete(f'FROM {self.item_type}_inv WHERE customid?==?{custom_id}')
        elif quantity > 1:
            self.db.update(
                f"INTO {self.item_type}_inv UPDATE quantity WHERE customid?==?{custom_id} TO {quantity - 1}")

    def selection_box(self, x, y):
        bg_rect = pygame.Rect(x - 200, y - 150, 400, 300)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def button(self, text, x, y, self_index, active_index, disabled):
        # bg_rect = self.selection_box(WIDTH / 2 - (ITEM_BOX_SIZE / 2), HEIGTH / 2 + 70, True)
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE if self_index == active_index else UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

        if disabled:
            self.button(' --- ', x, y, 5, active_index, False)

    def display(self):
        self.input()
        self.selection_cooldown()
        self.selection_box(WIDTH / 2, HEIGTH / 2)

        self.button('use', (WIDTH / 2), (HEIGTH / 2) - 20, 0, self.selection_index, self.disable_use)
        self.button('drop', (WIDTH / 2), (HEIGTH / 2) + 30, 1, self.selection_index, self.disable_drop)
