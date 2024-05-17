import pygame

from settings import TEXT_COLOR, UI_FONT, UI_FONT_SIZE, WIDTH, HEIGTH, UI_BG_COLOR, UI_BORDER_COLOR, UI_BORDER_COLOR_ACTIVE, STATUS_MENU_SIZE, ITEM_BOX_EQUIPMENT
from ids import item_name, item_path, menu_item_descriptions
from dialogues import dialogues


class DialogueMenu:
    def __init__(self, npc_name, db):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.db = db
        self.slot = self.db.get_database()
        # will query the quest progress by the npc name
        # dialogues will have other dialogues of the same npc like "solaire2", "solaire3" indicating the quest progress

        # selection system
        self.selection_time = pygame.time.get_ticks()
        self.can_move = False
        self.selection_index = 0

        self.active_text = ""
        self.text_active = False
        self.text_time = pygame.time.get_ticks()
        self.dialogues = dialogues[npc_name]
        self.dialogue_index = 0

        self.closed = False
        self.shopmenu_open = False

    def get_closed(self):
        return self.closed

    def button(self, text, x, y, button_id):
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
            if keys[pygame.K_DOWN] and self.selection_index < 2:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            elif keys[pygame.K_UP] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.trigger(self.selection_index)

            if keys[pygame.K_BACKSPACE] or keys[pygame.K_ESCAPE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.closed = True
                del self

    def trigger(self, index):
        if index == 0:
            self.text_time = pygame.time.get_ticks()
            self.active_text = self.dialogues[self.dialogue_index]
            self.text_active = True
        if index == 1:
            self.shopmenu_open = True
            self.shopmenu = ShopMenu(self.db)
        if index == 2:
            self.closed = True

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 170:
                self.can_move = True

    def text_cooldown(self):
        if self.text_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.text_time >= 2000:
                if self.dialogue_index < len(self.dialogues) - 1:
                    self.dialogue_index += 1
                    self.active_text = self.dialogues[self.dialogue_index]
                    self.text_time = pygame.time.get_ticks()
                else:
                    self.text_active = False
                    self.active_text = ""

    def text(self, text, x, y):
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(x, y))
        self.display_surface.blit(text_surf, text_rect)

    def draw_border(self, x, y, width, height):
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, rect, 3)
        return rect

    def display(self):
        self.selection_cooldown()
        self.text_cooldown()
        if self.text_active:
            self.text(self.active_text, WIDTH / 2, HEIGTH - 100)
        if not self.shopmenu_open:
            self.input()

        screen = self.draw_border(100, 100, 300, 500)

        self.button('talk', screen.x + 20, screen.y + 20, 0)
        self.button('trade', screen.x + 20, screen.y + 70, 1)
        self.button('quit', screen.x + 20, screen.y + 120, 2)

        if self.shopmenu_open and not self.shopmenu.get_closed():
            self.shopmenu.display()


class ShopMenu:
    def __init__(self, db):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        self.db = db

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

        self.query = [
            # id, itemid, pathid, quantity, price, descriptionid
            ['0', '2001', '2201', '4', '2500', '2001']
        ]

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

    def re_query(self, index, keep_index=False):
        type_list = ["consumable_inv", "none", "none", "none", "none", "none", "none", "none"]
        if not keep_index:
            self.selection_index = 0
        self.can_move = False
        self.selection_time = pygame.time.get_ticks()

        self.item_graphics = []
        self.type = type_list[index]
        if type_list[index] != "none":
            # self.query = doc.get(f"INDB slot1 FROM {type_list[index]} WHERE quantity?>=?0")
            self.get_items(self.query)
        else:
            self.index_list = [0]

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

            if keys[pygame.K_BACKSPACE] or keys[pygame.K_ESCAPE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.closed = True
                del self

    def trigger(self, index):
        print('buy stuff')

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
        bg_rect = pygame.Rect(x, y, STATUS_MENU_SIZE, STATUS_MENU_SIZE - 400)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

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

        # if self.type != "weapon_inv":
        #     self.text(self.query[button_index][6], item_rect.x + 40, item_rect.y + 40, True)

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
                self.text('required souls', 875, 171 + offset_y)
                self.text(self.query[i][4], 875, 221 + offset_y)
                self.draw_border(860, 161 + offset_y, 300, 120, False)
                offset_y += 122

        self.draw_border(100, 80, 765, 570, False)
