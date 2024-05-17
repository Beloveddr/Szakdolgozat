import pygame
from settings import UI_FONT, UI_FONT_SIZE, UI_BIGGER_FONT_SIZE, UI_BG_COLOR, UI_HUMANITY_ACTIVE_COLOR, HEALTH_COLOR, HEALTH_BAR_WIDTH, STAMINA_COLOR, BAR_HEIGHT, weapon_data, magic_data, TEXT_COLOR, UI_BORDER_COLOR, UI_BORDER_COLOR_ACTIVE, ITEM_BOX_SIZE, STAMINA_BAR_WIDTH
from ids import item_path


class UI:
    def __init__(self, db, player):
        # general
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.bigger_font = pygame.font.Font(UI_FONT, UI_BIGGER_FONT_SIZE)
        self.empty_image = pygame.image.load("../graphics/blocks/empty/64x64transparent.png").convert_alpha()

        self.db = db
        self.player = player
        self.slot = self.player.save_slot

        self.humanity_ui_color = UI_BG_COLOR
        if player.human:
            self.set_humanity_ui_color(UI_HUMANITY_ACTIVE_COLOR)

        # bar setup
        self.health_bar_rect = pygame.Rect(95, 30, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.stamina_bar_rect = pygame.Rect(95, 55, STAMINA_BAR_WIDTH, BAR_HEIGHT)
        # self.energy_bar_rect = pygame.Rect(95, 80, ENERGY_BAR_WIDTH, BAR_HEIGHT)

        # convert consumable dictionary
        self.consumable_quantites = []
        self.update_consumable_inventory()

        # convert weapon dictionary
        self.update_weapon_inventory()

        # convert magic dictionary
        self.update_magic_inventory()

    def set_humanity_ui_color(self, color):
        self.humanity_ui_color = color

    def update_weapon_inventory(self):
        self.left_hand_graphics = []
        self.right_hand_graphics = []
        query = self.db.get(f"FROM weapon_inv WHERE isequiped?==?1")
        item_index = 0
        if len(query) > 0:
            for i in query:
                location = query[item_index][1]
                # self.weapon_graphics.append(pygame.image.load(item_path[location]).convert_alpha())
                if i[3] == str(0) or i[3] == str(1):
                    self.right_hand_graphics.append(pygame.image.load(item_path[location]).convert_alpha())
                if i[3] == str(7) or i[3] == str(8):
                    self.left_hand_graphics.append(pygame.image.load(item_path[location]).convert_alpha())

                item_index += 1
        if len(self.left_hand_graphics) < 1:
            self.left_hand_graphics.append(self.empty_image.copy())
        if len(self.right_hand_graphics) < 1:
            self.right_hand_graphics.append(self.empty_image.copy())

    def update_consumable_inventory(self):
        self.consumable_graphics = []
        self.consumable_quantites = []
        query = self.db.get(f"FROM consumable_inv WHERE isequiped?==?1")
        item_index = 0
        if len(query) > 0:
            for i in query:
                location = query[item_index][1]
                self.consumable_graphics.append(pygame.image.load(item_path[location]).convert_alpha())
                self.consumable_quantites.append(query[item_index][5])
                item_index += 1
        else:
            self.consumable_graphics.append(self.empty_image.copy())
            self.consumable_quantites.append(' ')


    def update_magic_inventory(self):
        self.magic_graphics = []

        output = {}
        # going through the magic_hand's keys and give the element that's bigger than 0
        for inv_item in self.player.magic_hand.keys():
            output[inv_item] = {"graphic": magic_data[inv_item]["graphic"]}

        for magic in output.values():
            magic = pygame.image.load(magic['graphic']).convert_alpha()
            self.magic_graphics.append(magic)

    def show_bar(self, current, max_amount, bg_rect, color):
        # draw bg
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # converting stat to pixel
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # drawing the bar
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_souls(self, souls):
        text_surf = self.font.render(str(int(souls)), False, TEXT_COLOR)
        x = 1200
        y = 660
        text_rect = text_surf.get_rect(bottomright=(x, y))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def show_humanity(self, humanity):
        text_surf = self.bigger_font.render(str(int(humanity)), False, TEXT_COLOR)
        x = 37
        y = 30
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.circle(self.display_surface, self.humanity_ui_color, (50, 50), 30)
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.circle(self.display_surface, UI_BORDER_COLOR, (50, 50), 30, 3)

    def selection_box(self, left, top, has_switched):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if has_switched:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def consumable_overlay(self, consume_index, has_switched):
        bg_rect = self.selection_box(120, 600, has_switched)  # weapon
        consumable_surf = self.consumable_graphics[consume_index]
        consumable_rect = consumable_surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(consumable_surf, consumable_rect)

    def weapon_overlay(self, weapon_index, has_switched, hand):
        if hand == 'left':
            bg_rect = self.selection_box(37, 560, has_switched)  # weapon
            weapon_surf = self.left_hand_graphics[weapon_index]
            weapon_rect = weapon_surf.get_rect(center=bg_rect.center)

            self.display_surface.blit(weapon_surf, weapon_rect)
        elif hand == 'right':
            bg_rect = self.selection_box(203, 560, has_switched)  # weapon
            weapon_surf = self.right_hand_graphics[weapon_index]
            weapon_rect = weapon_surf.get_rect(center=bg_rect.center)

            self.display_surface.blit(weapon_surf, weapon_rect)

    def left_hand_overlay(self, weapon_index, has_switched):
        bg_rect = self.selection_box(37, 560, has_switched)  # weapon
        weapon_surf = self.left_hand_graphics[weapon_index]
        weapon_rect = weapon_surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(weapon_surf, weapon_rect)

    def magic_overlay(self, magic_index, has_switched):
        bg_rect = self.selection_box(120, 515, has_switched)  # weapon
        magic_surf = self.magic_graphics[magic_index]
        magic_rect = magic_surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(magic_surf, magic_rect)

    def consumable_info(self, active_consumable_quantity):
        text_surf = self.font.render(str(str(active_consumable_quantity)), False, TEXT_COLOR)
        x = 176
        y = 649
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def magic_info(self, active_magic_quantity, magic_index):
        if list(self.player.magic_hand)[magic_index] != 'none':
            text_surf = self.font.render(str(str(active_magic_quantity)), False, TEXT_COLOR)
            x = 176
            y = 564
            text_rect = text_surf.get_rect(topleft=(x, y))
            pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
            self.display_surface.blit(text_surf, text_rect)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def display(self, player):
        if player.update_ui:
            # print('updated')
            if player.update_consume_index:
                player.consume_index = 0
                self.player.consumable_inventory = self.db.get(f"FROM consumable_inv WHERE isequiped?==?1")
            if player.update_cons_items:
                self.player.consumable_inventory = self.db.get(f"FROM consumable_inv WHERE isequiped?==?1")
                player.update_cons_items = False

            if player.update_weapon_index:
                player.set_weapons()

            self.update_consumable_inventory()
            self.update_weapon_inventory()
            self.update_magic_inventory()
            player.update_ui = False
            player.update_consume_index = False

        self.show_bar(player.vitality, 400 + player.stats['vitality'] * 15, self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.endurance, 80 + (player.stats['endurance'] * 2), self.stamina_bar_rect, STAMINA_COLOR)

        self.show_humanity(player.humanity)
        self.show_souls(player.souls)

        self.consumable_overlay(player.consume_index, not player.can_switch_consume)
        self.weapon_overlay(player.weapon_index, not player.can_switch_right_hand, 'right')
        self.weapon_overlay(player.left_hand_index, not player.can_switch_left_hand, 'left')
        self.magic_overlay(player.magic_index, not player.can_switch_magic)

        self.consumable_info(player.get_active_consumable())
        self.magic_info(player.get_active_magic(), self.player.magic_index)

        # debug mouse position
        # print(str(pygame.mouse.get_pos()))
