import pygame

from docs import Document
from settings import TEXT_COLOR, UI_BG_COLOR, STATUS_MENU_SIZE, UI_BORDER_COLOR, UI_BORDER_COLOR_ACTIVE, WIDTH, HEIGTH
from main_settings import STATS_DICT


def query_players():
    ls = []
    # just some plays with the data to get a good result list
    for i in [1, 2, 3]:
        db = Document(f"slot{i}", ['player'])
        # query the empty slots and get the [0]th element to get a list of lists not list of lists of lists
        ls.append(db.get(f"FROM player WHERE stat?==?empty")[0])
        # overwrite the queried data, make id the level and the field to the name
        ls[i-1][0] = db.get(f"FROM player WHERE stat?==?level")[0][2]
        ls[i-1][1] = db.get(f"FROM player WHERE stat?==?name")[0][2]
    return ls


class SlotSelection:
    def __init__(self, action, font, chosen_class='', player_name='', ch_obj='None'):
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.font = font

        if player_name != '':
            self.ch_obj = ch_obj
            self.ch_obj.accept = False

        # item creation
        self.height = 60
        self.width = 300

        # main box
        self.box_x = 100
        self.box_y = 35

        self.small_border_x = self.box_x + 40
        self.small_border_y = self.box_y + 90

        # selection system
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True

        self.closed = False
        self.selected = False
        self.selection = ''
        self.chosen_class = chosen_class
        self.name = player_name

        self.slots = query_players()

        self.action = action

        self.ok_sound = pygame.mixer.Sound('../audio/menu/OK.wav')
        self.select_sound = pygame.mixer.Sound('../audio/menu/SELECT.wav')
        self.ok_sound.set_volume(0.4)
        self.select_sound.set_volume(0.4)

    def set_class(self, chosen_class):
        self.chosen_class = chosen_class

    def set_name(self, name):
        self.name = name

    def get_slot(self):
        return self.selection

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.selection_index < 3:
                self.selection_index += 1
                self.can_move = False
                self.select_sound.play()
                self.selection_time = pygame.time.get_ticks()

            elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.select_sound.play()
                self.selection_time = pygame.time.get_ticks()

            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.selection_index = 3
                self.can_move = False
                self.select_sound.play()
                self.selection_time = pygame.time.get_ticks()

            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                self.selection_index = 1
                self.can_move = False
                self.select_sound.play()
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.trigger(self.selection_index)

            if keys[pygame.K_BACKSPACE] or keys[pygame.K_ESCAPE]:
                if self.action == 'load':
                    self.action = 'quit'
                self.closed = True
                del self

    def trigger(self, index):
        self.ok_sound.play()
        if index == 0:
            self.selection = 'slot1'
        if index == 1:
            self.selection = 'slot2'
        if index == 2:
            self.selection = 'slot3'
        if index == 3 and self.action == "save":
            self.overwrite_slot(self.selection)
            # with open('../saves/last_slot.ini', 'w') as f:
            #     f.write(str(self.selection))

            self.selected = True
            self.closed = True
        elif index == 3 and self.action == "load":
            # with open('../saves/last_slot.ini', 'w') as f:
            #     f.write(str(self.selection))

            self.selected = True
            self.closed = True

    def overwrite_slot(self, slot):
        with open(f'dbs/{slot}/stats.ini', 'w') as f:
            f.write(STATS_DICT[self.chosen_class])

        with open(f'dbs/{slot}/player.ini', 'w') as f:
            f.write(f'[1, name, {self.name}];[2, class, {self.chosen_class}];[3, level, 10];[4, currenthp, 0];[5, souls, 0];[6, humanity, 0];[7, ishuman, False];[8, playermap, map2-1];[9, empty, no];')

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 200:
                self.can_move = True

    def selection_box(self, x, y):
        # bg_rect = pygame.Rect(x, y, STATUS_MENU_SIZE, STATUS_MENU_SIZE - 350)
        # box_rect = bg_rect.
        # pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        # pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        text_surf = self.font.render('', False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(STATUS_MENU_SIZE, STATUS_MENU_SIZE - 350))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(STATUS_MENU_SIZE, STATUS_MENU_SIZE - 350), 3)

    def center_box(self, text, width, height, x, y, id, index):
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(width, height))
        self.display_surface.blit(text_surf, text_rect)
        if index == id:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, text_rect.inflate(width, height), 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(width, height), 3)

    def button_centered(self, text, x, y):
        # bg_rect = self.selection_box(WIDTH / 2 - (ITEM_BOX_SIZE / 2), HEIGTH / 2 + 70, True)
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def button(self, text, width, height, x, y, index):
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        if index == 3:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, text_rect.inflate(width, height), 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(width, height), 3)

    def draw_border(self, x, y, width, height, is_active):
        rect = pygame.Rect(x, y, width, height)
        if is_active:
            color = UI_BORDER_COLOR_ACTIVE
        else:
            color = UI_BORDER_COLOR
        pygame.draw.rect(self.display_surface, color, rect, 3)

    def draw_text(self, text, size, x, y):
        text_surface = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display_surface.blit(text_surface, text_rect)

    def display(self):
        self.input()
        self.selection_cooldown()

        self.selection_box(WIDTH/2, HEIGTH/2)

        # self.button('Select Save Slot', self.box_x + 130, self.box_y + 40)
        x = 300
        for i in [0, 1, 2]:
            self.center_box(f'Select Save Slot{i+1}', 50, 200, x, 300, i, self.selection_index)
            # means not empty slot
            if self.slots[i][2] == 'no':
                self.draw_text(f'name: {self.slots[i][1]}', 1, x, 340)
                self.draw_text(f'level: {self.slots[i][0]}', 1, x, 370)
            x += 300

        self.button('accept', 100, 75, 600, 500, self.selection_index)

        if self.selection != '':
            self.draw_text(f'Selected slot: {self.selection}', 1, 600, 150)
        # self.draw_border(self.small_border_x, self.small_border_y, 600, 100, False)

        # self.button('select: up, down | enter: space | exit: backspace', 158, 620)

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        self.display()
        pygame.display.update()

