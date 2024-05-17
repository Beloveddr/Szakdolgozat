import pygame

from settings import WIDTH, HEIGTH, UI_FONT, UI_FONT_SIZE, TEXT_COLOR, UI_BG_COLOR, UI_BORDER_COLOR, ITEM_BOX_SIZE
from menu_status import MenuStatus
from menu_inventory import MenuInventory
from menu_equipment import MenuEquipment


class IgMenu:
    def __init__(self, db, player, create_consume):
        # general setup
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.display_surface = pygame.display.get_surface()
        self.db = db
        self.player = player
        self.create_consume = create_consume

        # child menus
        self.inventory_menu = None
        self.equipment_menu = None
        self.status_menu = None

        self.inventory_open = False
        self.equipment_open = False
        self.status_open = False

        self.attribute_nr = len(player.stats)
        self.attribute_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # selection system
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True

        # the cursor's base position that indicates the buttons
        self.cursor_rect_x = 950
        self.cursor_rect_y = 110

        self.quit_game = False

        bg_rect = self.selection_box(1000, 20)
        self.igtop_surf = pygame.image.load('../graphics/ingame_menu/igtop.jpg').convert_alpha()
        self.igtop_rect = self.igtop_surf.get_rect(center=bg_rect.center)

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_RIGHT] and self.selection_index < 3:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            elif keys[pygame.K_LEFT] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.trigger(self.selection_index)

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 150:
                self.can_move = True

    # trigger an event by index (values are made manually)
    def trigger(self, index):
        if index == 0:
            self.inventory_open = True
            self.inventory_menu = MenuInventory(self.db, self.player)
        if index == 1:
            self.equipment_open = True
            self.equipment_menu = MenuEquipment(self.db, "consumable", self.player, self.create_consume)
        if index == 2:
            self.status_open = True
            self.status_menu = MenuStatus(self.player)
        if index == 3:
            self.quit_game = True
            # pygame.quit()
            # sys.exit()

    def draw_text(self, text, size, x, y):
        text_surface = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def button(self, text, x_scale):
        # bg_rect = self.selection_box(WIDTH / 2 - (ITEM_BOX_SIZE / 2), HEIGTH / 2 + 70, True)
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        y = 36
        x = HEIGTH / 2 + x_scale
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def selection_box(self, x, y):
        bg_rect = pygame.Rect(x, y, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        # pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        # pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def show_menu(self):
        self.display_surface.blit(self.igtop_surf, self.igtop_rect)

    def display(self):
        self.player.menu_open = True
        # self.button('Continue', 70)
        if self.status_open:
            if self.status_menu.get_closed():
                self.status_open = False
            else:
                self.status_menu.display()
        elif self.inventory_open:
            if self.inventory_menu.get_closed():
                self.inventory_open = False
            else:
                self.inventory_menu.display()
        elif self.equipment_open:
            if self.equipment_menu.get_closed():
                self.equipment_open = False
            else:
                self.equipment_menu.display()
        else:
            self.input()
        self.show_menu()
        # self.button('Quit', 130)
        self.selection_cooldown()
        if self.selection_index == 0:
            self.draw_text('*', 15, self.cursor_rect_x, self.cursor_rect_y)
        elif self.selection_index == 1:
            self.draw_text('*', 15, self.cursor_rect_x + 59, self.cursor_rect_y)
        elif self.selection_index == 2:
            self.draw_text('*', 15, self.cursor_rect_x + 59 * 2, self.cursor_rect_y)
        elif self.selection_index == 3:
            self.draw_text('*', 15, self.cursor_rect_x + 59 * 3, self.cursor_rect_y)

