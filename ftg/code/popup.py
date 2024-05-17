import pygame
from settings import UI_FONT, UI_FONT_SIZE, UI_BIGGER_FONT_SIZE, POPUP_BAR_WIDTH, POPUP_BAR_HEIGHT, WIDTH, HEIGTH, UI_BG_COLOR, UI_BORDER_COLOR, TEXT_COLOR


class Popup:
    def __init__(self, player, item, item_quantity):
        self.display_surface = pygame.display.get_surface()
        # self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.bigger_font = pygame.font.Font(UI_FONT, UI_BIGGER_FONT_SIZE)

        # bar setup
        self.bar_rect = pygame.Rect(95, 30, POPUP_BAR_WIDTH, POPUP_BAR_HEIGHT)
        self.pop = False
        self.pop_time = 600
        self.pop_cooldown = 700

        self.player = player
        self.item = item
        self.item_quantity = item_quantity

        self.box_x = WIDTH / 2
        self.box_y = HEIGTH - 130

        self.box_width = 400
        self.box_height = 75

        if self.item_quantity != 0:
            self.pick_up_sound = pygame.mixer.Sound('../audio/pickup.wav')
            self.pick_up_sound.set_volume(0.02)
            self.pick_up_sound.play()

    def selection_box(self, x, y, width, height):
        bg_rect = pygame.Rect(x, y, width, height)
        bg_rect.center = (x, y)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def selection_box_picture(self, x, y):
        bg_rect = pygame.Rect(x, y, 100, self.box_height)
        bg_rect.center = (x, y)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def show_box(self):
        self.selection_box(self.box_x, self.box_y, self.box_width, self.box_height)
        self.selection_box(self.box_x - 23, self.box_y + 70, self.box_width, self.box_height - 40)

    def draw(self, text, size, x, y):
        text_surface = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display_surface.blit(text_surface, text_rect)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.pop:
            if current_time - self.pop_time >= self.pop_cooldown:
                self.pop = False

    def show_item(self, item):
        bg_rect = self.selection_box_picture(self.box_x - 200, self.box_y)
        surf = pygame.image.load('../graphics/full_img/' + str(item) + '_full.png')
        rect = surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(surf, rect)

    def display(self):
        self.show_box()
        self.draw(str(self.item), 20, self.box_x - 60, self.box_y)
        self.draw(str(self.item_quantity), 20, self.box_x + 150, self.box_y)
        self.show_item(str(self.item))
        self.draw('q: ok', 20, self.box_x - 23, self.box_y + 70)
        self.cooldowns()


class PopupText:
    def __init__(self, player, text):
        self.display_surface = pygame.display.get_surface()
        # self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.bigger_font = pygame.font.Font(UI_FONT, UI_BIGGER_FONT_SIZE)

        # bar setup
        self.bar_rect = pygame.Rect(95, 30, POPUP_BAR_WIDTH, POPUP_BAR_HEIGHT)
        self.pop = False
        self.pop_time = 600
        self.pop_cooldown = 700

        self.player = player
        self.text = text

        self.box_x = WIDTH / 2
        self.box_y = HEIGTH - 130

        self.box_width = 400
        self.box_height = 75

        self.pick_up_sound = pygame.mixer.Sound('../audio/pickup.wav')
        self.pick_up_sound.set_volume(0.02)
        self.pick_up_sound.play()

    def selection_box(self, x, y, width, height):
        bg_rect = pygame.Rect(x, y, width, height)
        bg_rect.center = (x, y)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def selection_box_picture(self, x, y):
        bg_rect = pygame.Rect(x, y, 100, self.box_height)
        bg_rect.center = (x, y)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def show_box(self):
        self.selection_box(self.box_x, self.box_y, self.box_width, self.box_height)
        self.selection_box(self.box_x, self.box_y + 70, self.box_width-40, self.box_height - 40)

    def draw(self, text, x, y):
        text_surface = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display_surface.blit(text_surface, text_rect)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.pop:
            if current_time - self.pop_time >= self.pop_cooldown:
                self.pop = False

    def display(self):
        self.show_box()
        self.draw(str(self.text), self.box_x, self.box_y)
        self.draw('q: ok', self.box_x, self.box_y + 70)
        self.cooldowns()
