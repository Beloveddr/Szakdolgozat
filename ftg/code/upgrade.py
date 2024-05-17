import pygame

from settings import UI_FONT, UI_FONT_SIZE, STATUS_MENU_SIZE, UI_BG_COLOR, UI_BORDER_COLOR, TEXT_COLOR, TEXT_COLOR_SELECTED, UPGRADE_BG_COLOR_SELECTED
from support import modify_stats_file


class Upgrade:
    def __init__(self, db, player):
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.db = db
        self.player = player
        self.attribute_nr = len(player.stats) - 1
        self.attribute_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # item creation
        self.height = 60
        self.width = 300
        self.create_items()

        # selection system
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True

        self.closed = False

    def get_closed(self):
        return self.closed

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.selection_index < self.attribute_nr - 1:
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
                self.item_list[self.selection_index].trigger(self.player)

            if keys[pygame.K_BACKSPACE]:
                self.closed = True
                del self

    def calculate_cost(self):
        return round(0.02 * (int(self.player.level)**3) + 3.06 * (int(self.player.level)**2) + 105.6 * int(self.player.level) - 895)

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 300:
                self.can_move = True

    def selection_box(self, x, y):
        bg_rect = pygame.Rect(x, y, STATUS_MENU_SIZE, STATUS_MENU_SIZE - 350)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def button_centered(self, text, x, y):
        # bg_rect = self.selection_box(WIDTH / 2 - (ITEM_BOX_SIZE / 2), HEIGTH / 2 + 70, True)
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def button(self, text, x, y):
        # bg_rect = self.selection_box(WIDTH / 2 - (ITEM_BOX_SIZE / 2), HEIGTH / 2 + 70, True)
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def create_items(self):
        self.item_list = []

        for item, index in enumerate(range(self.attribute_nr)):
            # horizontal position
            full_height = 330
            increment = full_height // self.attribute_nr
            top = (item * increment) + (increment - self.height) // 2

            # vertical position
            left = 150

            # create the object
            item = Item(left, top + 270, self.width, self.height, index, self.font, self.db)
            self.item_list.append(item)

    def display(self):
        self.input()
        self.selection_cooldown()

        self.selection_box(100, 35)

        self.button_centered(self.player.name, 300, 100)
        self.button('level           ' + str(self.player.level), 160, 150)
        self.button('souls       ' + str(self.player.souls), 160, 190)
        self.button('reqsouls    ' + str(self.calculate_cost()), 160, 230)

        for index, item in enumerate(self.item_list):
            # get attributes
            name = self.attribute_names[index]
            value = self.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = round(0.02 * (int(self.player.level)**3) + 3.06 * (int(self.player.level)**2) + 105.6 * int(self.player.level) - 895)
            item.display(self.display_surface, self.selection_index, name, value, max_value, cost)

        # we need space for other stuff
        # self.button('humanity    ' + str(self.player.humanity), 158, 610)

        self.button('select: up, down | enter: space | exit: backspace', 158, 620)

        self.button('vitality     ' + str(round(self.player.vitality)) + '/' + str(400 + (self.player.stats['vitality'] * 15)), 500, 200)
        self.button('attunement    ' + str(self.player.attunement), 500, 250)
        self.button('endurance     ' + str(round(self.player.endurance)) + '/' + str(80 + (2 * self.player.stats['endurance'])), 500, 300)
        self.button('strength    ' + str(round(self.player.strength)), 500, 350)
        self.button('dexterity    ' + str(round(self.player.dexterity)), 500, 400)
        self.button('inteligence      ' + str(round(self.player.inteligence)), 500, 450)


class Item:
    def __init__(self, l, t, w, h, index, font, db):
        self.rect = pygame.rect.Rect(l, t, w, h)
        self.index = index
        self.font = font
        self.db = db
        self.display_surface = pygame.display.get_surface()

    # ds based level upgrade cost calculation
    def calculate_cost(self, player):
        return round(0.02 * (int(player.level)**3) + 3.06 * (int(player.level)**2) + 105.6 * int(player.level) - 895)

    def display_names(self, surface, name, cost, selected):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        # title
        title_surf = self.font.render(name + ':', False, color)
        title_rect = title_surf.get_rect(topleft=self.rect.topleft + pygame.math.Vector2(20, 20))

        # cost
        # cost_surf = self.font.render('upgrade cost: ' + f'{int(cost)}', False, color)
        # cost_rect = cost_surf.get_rect(topleft=self.rect.topleft + pygame.math.Vector2(20, 50))

        # draw
        surface.blit(title_surf, title_rect)
        # surface.blit(cost_surf, cost_rect)

    def display_values(self, surface, value, max_value, selected):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        # title
        title_surf = self.font.render('    ' + str(value), False, color)
        title_rect = title_surf.get_rect(topleft=self.rect.topleft + pygame.math.Vector2(190, 20))

        # draw
        surface.blit(title_surf, title_rect)

    def trigger(self, player):
        cost = self.calculate_cost(player)

        upgrade_attribute = list(player.stats.keys())[self.index]

        if player.souls >= cost and player.stats[upgrade_attribute] < 99 and player.stats[upgrade_attribute] < player.max_stats[upgrade_attribute]:
            player.level += 1
            player.souls -= cost
            # instead of this
            player.stats[upgrade_attribute] += 1

            # copy the current stats from file and write the new list into the file
            curr_stats = player.set_stats()
            curr_stats[upgrade_attribute] += 1

            # replacing the single quotes for double quotes because we are working with json
            modified = str(curr_stats).replace("'", '"')
            modify_stats_file(f'dbs/{player.save_slot}/stats.ini', modified)

            # modify_ini_file('../saves/plyr/lvl.ini', "level", player.level)
            self.db.update(f"INTO player UPDATE value WHERE stat?==?level TO {player.level}")
            # modify_ini_file('../saves/plyr/lvl.ini', "souls", player.souls)
            self.db.update(f"INTO player UPDATE value WHERE stat?==?souls TO {player.souls}")

            # update player stats
            player.update_stats()

        if player.stats[upgrade_attribute] > player.max_stats[upgrade_attribute]:
            player.stats[upgrade_attribute] = player.max_stats[upgrade_attribute]

    def display(self, surface, selection_num, name, value, max_value, cost):
        if self.index == selection_num:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, cost, self.index == selection_num)
        self.display_values(surface, value, max_value, self.index == selection_num)
