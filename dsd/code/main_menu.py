import pygame
import sys
from main_settings import *


class MainMenu:
    def __init__(self, screen, display_surface, font, bg_image, faded_in=False):
        self.screen = screen
        self.font = font
        self.display_surface = display_surface
        self.background_image = bg_image

        # selection system
        self.selection_index = 0
        self.selection_time = pygame.time.get_ticks()
        self.can_move = False

        # the cursor's base position that indicates the buttons
        self.cursor_rect_x = 540
        self.cursor_rect_y = 410

        self.closed = False
        self.location = ''

        self.ok_sound = pygame.mixer.Sound('../audio/menu/OK.wav')
        self.select_sound = pygame.mixer.Sound('../audio/menu/SELECT.wav')
        self.ok_sound.set_volume(0.4)
        self.select_sound.set_volume(0.4)

        self.faded_in = faded_in
        # if not self.faded_in:
        #     self.sekiraw_img = pygame.image.load('../graphics/main_menu/sekiraw.png').convert_alpha()

    def fade_in(self):
        fade = pygame.Surface((WIDTH, HEIGTH))
        fade.fill((0, 0, 0))
        # fade out
        # for alpha in range(0, 300):
        for alpha in range(300, -1, -1):
            fade.set_alpha(alpha)
            # pygame.draw.rect(self.screen, (255,0,0), (200,300,200,200), 0)
            # pygame.draw.rect(self.screen, (0,255,0), (500,300,200,200), 0)
            self.screen.blit(self.background_image, (0, 0))

            self.draw_text(
                'FromSoftware is not affiliated with this project.',
                640, 630
            )
            self.draw_text(
                'All content is the property of their respective owners',
                640, 660
            )

            self.display()
            self.screen.blit(fade, (0, 0))
            pygame.display.update()
            # pygame.time.delay(2)

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.selection_cooldown()
        self.input()

        # self.screen.fill(WATER_COLOR)
        self.screen.blit(self.background_image, (0, 0))

        self.draw_text(
            'FromSoftware is not affiliated with this project.',
            640, 630
        )
        self.draw_text(
            'All content is the property of their respective owners',
            640, 660
        )

        if not self.faded_in:
            self.fade_in()
            self.faded_in = True

        self.display()
        pygame.display.update()

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def button(self, text, y_scale):
        # bg_rect = self.selection_box(WIDTH / 2 - (ITEM_BOX_SIZE / 2), HEIGTH / 2 + 70, True)
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        x = WIDTH / 2 - (text_surf.get_size()[0] / 2)
        y = HEIGTH / 2 + y_scale
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.selection_index < 3:
                self.select_sound.play()
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            elif (keys[pygame.K_w] or keys[pygame.K_UP]) and self.selection_index >= 1:
                self.select_sound.play()
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
            if current_time - self.selection_time >= SELECTION_COOLDOWN_TIME:
                self.can_move = True

    def trigger(self, index):
        if index == 0:
            self.location = 'character_creation'
        if index == 1:
            # self.slot_select = SlotSelection('load')
            self.location = 'slot_selection'
        if index == 2:
            self.location = 'game'
            # self.save_slot = self.last_slot()
            # self.level = Level(self.save_slot)
        if index == 3:
            pygame.quit()
            sys.exit()

        self.ok_sound.play()
        self.closed = True

    def display(self):
        self.button('New game', 40)
        self.button('Load game', 100)
        self.button('Continue', 160)
        self.button('Quit', 220)

        if self.selection_index == 0:
            self.draw_text('*', self.cursor_rect_x, self.cursor_rect_y)
        elif self.selection_index == 1:
            self.draw_text('*', self.cursor_rect_x, self.cursor_rect_y + 60)
        elif self.selection_index == 2:
            self.draw_text('*', self.cursor_rect_x, self.cursor_rect_y + 120)
        elif self.selection_index == 3:
            self.draw_text('*', self.cursor_rect_x, self.cursor_rect_y + 180)


class CharacterCreation:
    def __init__(self, screen, display_surface, font, image):
        self.screen = screen
        self.font = font
        self.smaller_font = pygame.font.Font(UI_FONT, UI_SMALLER_FONT_SIZE)
        self.display_surface = display_surface
        self.character_selection_image = image

        # selection system
        self.selection_index = 0
        self.selection_time = pygame.time.get_ticks()
        self.can_move = False

        self.player_name = ''
        self.player_class = ''
        self.player_gift = ''
        self.active_text = False
        self.active_class = False
        self.active_gift = False

        self.class_tab_active = False
        self.class_tab_selection_index = 0
        self.lock_chosen_class = False
        self.chosen_class = 0

        self.gift_tab_active = False
        self.gift_tab_selection_index = 0

        # the cursor's base position that indicates the buttons
        self.cursor_rect_x = 168
        self.cursor_rect_y = 190

        self.closed = False
        self.accept = False
        self.location = ''

        self.ok_sound = pygame.mixer.Sound('../audio/menu/OK.wav')
        self.select_sound = pygame.mixer.Sound('../audio/menu/SELECT.wav')
        self.ok_sound.set_volume(0.4)
        self.select_sound.set_volume(0.4)

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # going back to main
                if event.key == pygame.K_ESCAPE:
                    self.closed = True
                elif not self.active_text:
                    if event.key == pygame.K_BACKSPACE:
                        self.closed = True
                else:
                    if self.active_text:
                        if event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        else:
                            if event.unicode in VALID_INPUT_LIST and len(self.player_name) < 12:
                                self.player_name += str(event.unicode)

        self.character_creation_update()

        pygame.display.update()

    def trigger(self, index):
        if index == 0:
            self.active_text = not self.active_text
            if not self.active_text:
                self.ok_sound.play()
        if index == 1:
            self.ok_sound.play()
            self.active_class = not self.active_class
            self.class_tab_active = not self.class_tab_active
            if self.class_tab_active:
                self.chosen_class = 0
        if index == 2:
            self.ok_sound.play()
            self.active_gift = not self.active_gift
            self.gift_tab_active = not self.gift_tab_active
        if index == 3:
            if self.player_name != '' and self.player_class != '' and self.player_gift != '':
                self.ok_sound.play()
                self.accept = True

    def class_tab_trigger(self, index):
        self.ok_sound.play()
        self.player_class = CLASS_LIST[index]
        self.class_tab_selection_index = 0
        # self.chosen_class = 0

    def gift_tab_trigger(self, index):
        self.ok_sound.play()
        self.player_gift = GIFT_LIST[index]
        self.gift_tab_selection_index = 0

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if self.class_tab_active:
                if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.class_tab_selection_index < len(CLASS_LIST) - 1:
                    self.class_tab_selection_index += 1
                    self.chosen_class += 1
                    self.can_move = False
                    self.select_sound.play()
                    self.selection_time = pygame.time.get_ticks()

                if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.class_tab_selection_index >= 1:
                    self.class_tab_selection_index -= 1
                    self.chosen_class -= 1
                    self.can_move = False
                    self.select_sound.play()
                    self.selection_time = pygame.time.get_ticks()

                # class picking space
                if keys[pygame.K_SPACE]:
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()
                    self.class_tab_trigger(self.class_tab_selection_index)

            if self.gift_tab_active:
                if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.gift_tab_selection_index < len(GIFT_LIST) - 1:
                    self.gift_tab_selection_index += 1
                    self.can_move = False
                    self.select_sound.play()
                    self.selection_time = pygame.time.get_ticks()

                if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.gift_tab_selection_index >= 1:
                    self.gift_tab_selection_index -= 1
                    self.can_move = False
                    self.select_sound.play()
                    self.selection_time = pygame.time.get_ticks()
                # gift picking space
                if keys[pygame.K_SPACE]:
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()
                    self.gift_tab_trigger(self.gift_tab_selection_index)
            if not self.active_text and not self.active_class and not self.active_gift:
                if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.selection_index < 3:
                    self.selection_index += 1
                    self.can_move = False
                    self.select_sound.play()
                    self.selection_time = pygame.time.get_ticks()

                if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.selection_index >= 1:
                    self.selection_index -= 1
                    self.can_move = False
                    self.select_sound.play()
                    self.selection_time = pygame.time.get_ticks()

                # entering
                if keys[pygame.K_SPACE]:
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()
                    self.trigger(self.selection_index)
            # quitting
            else:
                if keys[pygame.K_SPACE]:
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()
                    self.trigger(self.selection_index)

    def creator_box(self):
        # bg_rect = pygame.Rect(CREATOR_BOX_X, CREATOR_BOX_Y, WIDTH - 200, HEIGTH - 100)
        # pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        # pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        self.display_surface.blit(self.character_selection_image, (CREATOR_BOX_X, CREATOR_BOX_Y))

    def button_x_y(self, text, x, y, is_active=False):
        # bg_rect = self.selection_box(WIDTH / 2 - (ITEM_BOX_SIZE / 2), HEIGTH / 2 + 70, True)
        text_surf = self.font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        if is_active:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, text_rect.inflate(17, 17), 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_border(self, x, y, width, height, is_active):
        rect = pygame.Rect(x, y, width, height)
        if is_active:
            color = UI_BORDER_COLOR_ACTIVE
        else:
            color = UI_BORDER_COLOR
        pygame.draw.rect(self.screen, color, rect, 3)

    def button_x_y_smaller_font(self, text, x, y, is_active=False):
        text_surf = self.smaller_font.render(str(text), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topleft=(x, y))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
        self.display_surface.blit(text_surf, text_rect)
        if is_active:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, text_rect.inflate(17, 17), 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)

    def show_active_character(self, chosen_class):
        if chosen_class == 0:
            current_class = "Warrior"
        if chosen_class == 1:
            current_class = "Knight"
        else:
            current_class = "Warrior"
        image = pygame.image.load('../graphics/character_selection/' + str(current_class) + '.png')
        self.display_surface.blit(image, (CREATOR_BOX_X + 670, CREATOR_BOX_Y + 100))

    def active_class_stats(self, class_index):
        y_offset = 0
        for key, value in CLASS_DICT[class_index].items():
            self.button_x_y_smaller_font(str(key) + ': ' + str(value), CREATOR_BOX_X + 100,
                                         CREATOR_BOX_Y + 330 + y_offset)
            y_offset += 30

    def button_x_y_linebreak(self, text, x, y):
        lines = 1
        list = []
        for i in text:
            if i == '/':
                lines += 1
                list = text.split('/')

        if lines == 1:
            list.append(text)

        y_offset = 0
        for j in range(lines):
            text_surf = self.font.render(str(list[j]), False, TEXT_COLOR)
            text_rect = text_surf.get_rect(topleft=(x, y + y_offset))
            # pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(17, 17))
            self.display_surface.blit(text_surf, text_rect)
            # pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(17, 17), 3)
            y_offset += 40

        self.draw_border(x - 15, y - 15, 330, y_offset + 13, False)

    def small_window(self, x, y, width, height):
        text_surf = self.font.render('', False, TEXT_COLOR)
        text_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect)
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect, 3)

    def draw_class_options(self):
        self.small_window(CREATOR_BOX_X + 300, CREATOR_BOX_Y + 50, 350, 600)
        incr_y = 0
        y_pos = CREATOR_BOX_Y + 100
        self.draw_text('*', CREATOR_BOX_X + 332, (y_pos + 40 * self.class_tab_selection_index) + 10)
        for i in CLASS_LIST:
            self.button_x_y(i, CREATOR_BOX_X + 370, y_pos + incr_y, False)
            incr_y += 40

        self.button_x_y_linebreak(CLASS_DESCRIPTIONS[self.class_tab_selection_index], CREATOR_BOX_X + 326, 570)

    def draw_gift_options(self):
        self.small_window(CREATOR_BOX_X + 300, CREATOR_BOX_Y + 50, 350, 600)
        incr_y = 0
        y_pos = CREATOR_BOX_Y + 100
        self.draw_text('*', CREATOR_BOX_X + 332, (y_pos + 40 * self.gift_tab_selection_index) + 10)
        for i in GIFT_LIST:
            self.button_x_y(i, CREATOR_BOX_X + 370, y_pos + incr_y, False)
            incr_y += 40

        self.button_x_y_linebreak(GIFT_DESCRIPTIONS[self.gift_tab_selection_index], CREATOR_BOX_X + 326, 570)

    def character_creation_update(self):
        self.screen.fill(pygame.color.Color(0, 0, 0))
        self.input()
        self.selection_cooldown()

        self.creator_box()
        self.button_x_y('Create character', CREATOR_BOX_X + 140, CREATOR_BOX_Y + 40)

        if self.selection_index == 0:
            self.draw_text('*', self.cursor_rect_x, self.cursor_rect_y)
        elif self.selection_index == 1:
            self.draw_text('*', self.cursor_rect_x, self.cursor_rect_y + 40)
        elif self.selection_index == 2:
            self.draw_text('*', self.cursor_rect_x, self.cursor_rect_y + 80)

        self.draw_border(CREATOR_BOX_X + 50, CREATOR_BOX_Y + 100, 500, 200, False)

        self.draw_border(185, 175, 200, 35, self.active_text)

        self.button_x_y('Class' if self.player_class == '' else self.player_class, CREATOR_BOX_X + 93,
                        CREATOR_BOX_Y + 170, self.active_class)

        self.button_x_y('Gift' if self.player_gift == '' else self.player_gift, CREATOR_BOX_X + 93, CREATOR_BOX_Y + 210,
                        self.active_gift)

        self.button_x_y('Accept', CREATOR_BOX_X + 93, CREATOR_BOX_Y + 250, True if self.selection_index == 3 else False)

        surf = self.font.render(self.player_name, True, TEXT_COLOR)
        self.screen.blit(surf, (195, 181))

        # stats
        self.draw_border(CREATOR_BOX_X + 50, CREATOR_BOX_Y + 310, 230, 300, False)
        self.active_class_stats(self.chosen_class)

        # character graphic
        self.draw_border(CREATOR_BOX_X + 670, CREATOR_BOX_Y + 100, 350, 510, False)
        self.show_active_character(self.chosen_class)

        # inventory ui
        self.draw_border(CREATOR_BOX_X + 300, CREATOR_BOX_Y + 310, 350, 300, False)

        # controls
        self.button_x_y('Select: UP, down | enter: space | exit: esc', 108, 680)

        # active elements on top
        if self.active_class:
            self.draw_class_options()
        if self.active_gift:
            self.draw_gift_options()

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= SELECTION_COOLDOWN_TIME_CH:
                self.can_move = True
