import pygame
from settings import UI_FONT, UI_FONT_SIZE, TEXT_COLOR, UI_BORDER_COLOR, STATUS_MENU_SIZE, UI_BG_COLOR


class MenuStatus:
    def __init__(self, player):
        # general setup
        # self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attribute_nr = len(player.stats)
        self.attribute_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # selection system
        self.can_move = True

        # the cursor's base position that indicates the buttons
        self.cursor_rect_x = 950
        self.cursor_rect_y = 110

        self.closed = False

    def get_closed(self):
        return self.closed

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_BACKSPACE]:
                self.closed = True
                del self

    # trigger an event by index (values are made manually)
    def trigger(self, index):
        if index == 0:
            del self

    def draw_text(self, text, size, x, y):
        text_surface = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display_surface.blit(text_surface, text_rect)

    def button(self, text, x, y):
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
        # return bg_rect

    def show_status_box(self):
        self.selection_box(100, 10)

    def display(self):
        self.show_status_box()
        self.button(self.player.name, 200, 200)
        self.button('level      ' + str(self.player.level), 200, 250)
        self.button('Vitality     ' + str(round(self.player.vitality)) + '/' + str(400 + (self.player.stats['vitality'] * 15)), 500, 200)
        self.button('attunement     ' + str(round(self.player.attunement)), 500, 250)
        self.button('endurance    ' + str(round(self.player.endurance)) + '/' + str(80 + (2 * self.player.stats['endurance'])), 500, 300)
        self.button('strength     ' + str(round(self.player.strength)), 500, 350)
        self.button('dexterity      ' + str(round(self.player.dexterity)), 500, 400)
        self.button('inteligence      ' + str(round(self.player.inteligence)), 500, 400)

        self.input()
