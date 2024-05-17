import pygame
import sys

from docs import Document

from settings import *
from level import Level
from slot_selection import SlotSelection
from main_menu import MainMenu, CharacterCreation


class GameState:
    def __init__(self, theme_music):
        # print("Creating Main - main.py ~ 14")
        pygame.mouse.set_visible(False)
        #level generic stuff
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.smaller_font = pygame.font.Font(UI_FONT, UI_SMALLER_FONT_SIZE)

        # starting state
        self.state = 'main_menu'
        # self.state = 'editor'
        self.save_slot = 'slot1'

        # database
        self._tables = ['player', 'ground_objects', 'doors', 'chests', 'weapon_inv', 'consumable_inv', 'armor_inv']
        self.db = Document(self.save_slot, self._tables)

        self.level = Level(self.db)

        # self.clock = clock
        # self.fps_font = pygame.font.SysFont("Arial", 30, bold=True)

        surface = pygame.image.load('../graphics/tilemap/icon.png').convert_alpha()
        pygame.display.set_icon(surface)

        self.background_image = pygame.image.load('../graphics/main_menu/title_image.jpg')
        self.character_selection_image = pygame.image.load('../graphics/character_selection/bg.png')

        # ui generic stuff
        self.display_surface = pygame.display.get_surface()

        self.main_menu = MainMenu(self.screen, self.display_surface, self.font, self.background_image)

        self.theme_music = theme_music

    # shows current fps for test reasons
    # def fps_counter(self):
    #     fps = str(int(self.clock.get_fps()))
    #     fps_t = self.fps_font.render(fps, True, pygame.Color("RED"))
    #     self.screen.blit(fps_t, (WIDTH - 100, 50))

    def main_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.level.player_got_item = False
                    self.level.toggle_bonfire_menu()
                    if self.level.bonfire_menu is not None:
                        self.level.bonfire_menu.alert = False
                    self.level.alert = None
                if event.key == pygame.K_ESCAPE:
                    self.level.ESC_actions()
                if event.key == pygame.K_q:
                    if self.level.alert:
                        self.level.alert = False
                    # if self.level.player_got_item:
                    #     self.level.player_got_item = False
                    elif self.level.player_died:
                        self.db.update(f"INTO player UPDATE value WHERE stat?==?currenthp TO 0")
                        # reload the level at the level's current slot
                        self.level.__init__(self.db)

        # self.screen.fill(WATER_COLOR)
        self.level.run()
        # self.fps_counter()
        self.level.check_death()
        # debug("Hello")
        pygame.display.update()

        if self.level.closed:
            # self.level = Level('slot1')
            del self.level
            self.theme_music.play()
            self.main_menu = MainMenu(self.screen, self.display_surface, self.font, self.background_image, True)
            self.state = 'main_menu'

    def state_manager(self):
        if self.state == 'main_menu':
            self.main_menu.run()
            # if main menu closed, delete it, make a new one so we can get back to it, and create the slot obj
            if self.main_menu.closed:
                self.state = self.main_menu.location
                if self.state == 'slot_selection':
                    self.slot_select = SlotSelection('load', self.font)
                if self.state == 'character_creation':
                    self.character_creation = CharacterCreation(self.screen, self.display_surface, self.font, self.character_selection_image)
                if self.state == 'game':
                    self.theme_music.fadeout(4000)
                    self.level = Level(self.db)

                del self.main_menu
                # self.main_menu = MainMenu(self.screen, self.display_surface, self.font, self.background_image)

        if self.state == 'game':
            self.main_game()
        if self.state == 'editor':
            self.main_game()
        if self.state == 'character_creation':
            self.character_creation.run()
            if self.character_creation.closed:
                del self.character_creation
                self.main_menu = MainMenu(self.screen, self.display_surface, self.font, self.background_image, True)
                self.state = 'main_menu'
            elif self.character_creation.accept:
                self.slot_select = SlotSelection('save', self.font, self.character_creation.chosen_class, self.character_creation.player_name, self.character_creation)
                self.state = 'slot_selection'
        if self.state == 'slot_selection':
            if not self.slot_select.closed:
                self.slot_select.run()
                if self.slot_select.selected:
                    self.save_slot = self.slot_select.selection
                    self.db.set_database(self.save_slot, self._tables)
            # if self.slot_select.closed and self.save_slot.action == 'load':
            #     self.state = 'main_menu'
            else:
                # if the action is 'load' return to the menu, if not return to ch creation
                if self.slot_select.action == 'load':
                    if self.slot_select.selected:
                        self.state = 'game'
                        self.save_slot = self.slot_select.selection
                        self.db.set_database(self.save_slot, self._tables)
                        self.theme_music.fadeout(4000)
                        self.level = Level(self.db)
                    else:
                        self.state = 'main_menu'
                elif self.slot_select.action == 'save':
                    if self.slot_select.selected:
                        self.state = 'game'
                        self.save_slot = self.slot_select.selection
                        self.db.set_database(self.save_slot, self._tables)
                        self.theme_music.fadeout(4000)
                        self.level = Level(self.db)
                    else:
                        self.state = 'character_creation'
                elif self.slot_select.action == 'quit':
                    self.main_menu = MainMenu(self.screen, self.display_surface, self.font, self.background_image, True)
                    self.state = 'main_menu'
                # self.character_creation()

    def last_slot(self):
        with open('../global/last_slot.ini', 'r') as f:
            return f.read()


class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('Dark Souls Demastered')

        surface = pygame.image.load('../graphics/tilemap/icon.png').convert_alpha()
        pygame.display.set_icon(surface)

        self.clock = pygame.time.Clock()

        # self.level = Level()

        # sound
        theme_sound = pygame.mixer.Sound('../audio/menu/THEME.wav')
        theme_sound.set_volume(0.4)
        theme_sound.play(loops=-1)

        self.game_state = GameState(theme_sound)

    def run(self):
        while True:
            # calling the state_manager to manage the game states
            self.game_state.state_manager()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
