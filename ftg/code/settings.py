# game setup
WIDTH = 1280
HEIGTH = 720

CREATOR_BOX_X = 100
CREATOR_BOX_Y = 50

VALID_INPUT_LIST = ['_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                    't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

FPS = 60
TILESIZE = 64

HITBOX_OFFSET = {
    'player': -26,
    'objects': -40,
    'grass': -10,
    'floor': 0,
    'invisible': 0}

# ui
POPUP_BAR_HEIGHT = 50
POPUP_BAR_WIDTH = 300

BAR_HEIGHT = 20
BOSS_BAR_HEIGHT = 25
HEALTH_BAR_WIDTH = 200
BOSS_HEALTH_BAR_WIDTH = 600
STAMINA_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
ITEM_BOX_EQUIPMENT = 120
STATUS_MENU_SIZE = 1100
STATUS_MENU_SIZE_Y = 750
UI_FONT = '../graphics/font/joystix.ttf'
UI_FONT_SIZE = 18
UI_SMALLER_FONT_SIZE = 12
UI_BIGGER_FONT_SIZE = 32

# general colors
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_HUMANITY_ACTIVE_COLOR = '#666666'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# ui colors
HEALTH_COLOR = 'red'
STAMINA_COLOR = 'orange'
ENERGY_COLOR = 'blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

# upgrade menu
TEXT_COLOR_SELECTED = '#111111'
BAR_COLOR = '#EEEEEE'
BAR_COLOR_SELECTED = '#111111'
UPGRADE_BG_COLOR_SELECTED = '#EEEEEE'

ENTITY_UPDATE_DISTANCE = 1200

BONFIRE_MENU_LIST = ['level up', 'attune magic', 'covenant', 'kindle', 'reverse hollowing']

ground_object_ids = {
    '200': 'Key to somewhere',
    '201': 'Key to the abyss',
    '202': 'rapier',
    '203': 'humanity'
}

opener_ids = {
    'map2-1': 'Key to the abyss'
}

locations_db = {
    'map5-0': 'map2-0',
    'map2-0': 'map5-0',
    'map2-1': 'map5-1',
    'map5-1': 'map2-1',
    'map5-2': 'map6-0',
    'map6-0': 'map5-2',
    'map6-1': 'map6-2',
    'map6-2': 'map6-1'
}

locked_doors = [
    'map2-1',
    'map6-1'
]

# stuck doors have to be in locked doors
stuck_doors = [
    'map6-1'
]

unlocker_doors = {
    'map6-2': 'map6-1'
}

# consumables
consumable_data = {
    'potion': {'cooldown': 250, 'heal': 200, 'graphic': '../graphics/consumables/potion/full.png'},
    'humanity': {'cooldown': 100, 'heal': 9999, 'graphic': '../graphics/consumables/humanity/full.png'}
}

# weapons
weapon_data = {
    'broken_straight_sword': {'cooldown': 100, 'damage': 15,
                              'graphic': '../graphics/weapons/broken_straight_sword/full.png'},
    'black_knight_halberd': {'cooldown': 400, 'damage': 30,
                             'graphic': '../graphics/weapons/black_knight_halberd/full.png'},
    'hand_axe': {'cooldown': 300, 'damage': 2000,
                 'graphic': '../graphics/weapons/hand_axe/full.png'},
    'battle_axe': {'cooldown': 300, 'damage': 10,
                 'graphic': '../graphics/weapons/battle_axe/full.png'},
    'rapier': {'cooldown': 50, 'damage': 8,
               'graphic': '../graphics/weapons/rapier/full.png'},
    'sai': {'cooldown': 80, 'damage': 10,
            'graphic': '../graphics/weapons/sai/full.png'},
    'wand': {'cooldown': 80, 'damage': 1,
             'graphic': '../graphics/weapons/wand/full.png'},
    'bow': {'cooldown': 80, 'damage': 1,
             'graphic': '../graphics/weapons/bow/full.png'},
    'none': {'cooldown': 80, 'damage': 1,
             'graphic': '../graphics/weapons/none/full.png'}
}

boss_weapon_data = {
    'sai': {'cooldown': 80, 'damage': 10, 'graphic': '../graphics/weapons/sai/full.png'}
}

# magic
magic_data = {
    'flame': {
        'strength': 5,
        'name': 'Fire Surge',
        'type': 'pyromancy',
        'uses': 3,
        'int': 0,
        'fth': 0,
        'graphic': '../graphics/particles/flame/fire.png'},
    'heal': {
        'strength': 20,
        'name': 'boundful sunlight',
        'type': 'miracle',
        'uses': 3,
        'int': 0,
        'fth': 5,
        'graphic': '../graphics/particles/heal/heal.png'},
    'fart': {
        'strength': 20,
        'name': 'soothing Sunlight',
        'type': 'sorcery',
        'uses': 17,
        'int': 0,
        'fth': 10,
        'graphic': '../graphics/particles/fart/fart.png'},
    'fart2': {
        'strength': 20,
        'name': 'Circle',
        'type': 'sorcery',
        'uses': 12,
        'int': 0,
        'fth': 10,
        'graphic': '../graphics/particles/fart2/fart2.png'},
    'fart3': {
        'strength': 20,
        'name': 'Lines',
        'type': 'miracle',
        'uses': 25,
        'int': 0,
        'fth': 10,
        'graphic': '../graphics/particles/fart3/fart3.png'},
    'fart4': {
        'strength': 20,
        'name': 'Kaka?',
        'type': 'miracle',
        'uses': 7,
        'int': 0,
        'fth': 10,
        'graphic': '../graphics/particles/fart4/fart4.png'},
    'fart5': {
        'strength': 20,
        'name': 'Something',
        'type': 'miracle',
        'uses': 3,
        'int': 0,
        'fth': 10,
        'graphic': '../graphics/particles/fart5/fart5.png'},
    'none': {
        'strength': 0,
        'name': '',
        'type': '',
        'uses': '',
        'int': '',
        'fth': '',
        'graphic': '../graphics/particles/none/64none.png'}
}

magic_indexes = {
    0: "flame",
    1: "heal",
    2: "fart",
    3: "fart2",
    4: "fart3",
    5: "fart4",
    6: "fart5"
}

magic_properties = {
    'flame':
        {
            'name': 'Fire Surge',
            'type': 'Pyromancy',
            'uses': 80,
            'int': 0,
            'fth': 0,
            'graphic': '../graphics/particles/flame/fire.png'
        },
    'heal':
        {
            'name': 'boundful sunlight',
            'type': 'Miracle',
            'uses': 2,
            'int': 0,
            'fth': 5,
            'graphic': '../graphics/particles/heal/heal.png'
        },
    'fart':
        {
            'name': 'soothing Sunlight',
            'type': 'Miracle',
            'uses': 3,
            'int': 0,
            'fth': 10,
            'graphic': '../graphics/particles/fart/fart.png'
        },
    'fart2':
        {
            'name': 'Circle',
            'type': 'sorcery',
            'uses': 3,
            'int': 0,
            'fth': 10,
            'graphic': '../graphics/particles/fart2/fart2.png'
        },
    'fart3':
        {
            'name': 'Lines',
            'type': 'miracle',
            'uses': 3,
            'int': 0,
            'fth': 10,
            'graphic': '../graphics/particles/fart3/fart3.png'
        },
    'fart4':
        {
            'name': 'Something',
            'type': 'miracle',
            'uses': 3,
            'int': 0,
            'fth': 10,
            'graphic': '../graphics/particles/fart4/fart4.png'
        },
    'fart5':
        {
            'name': 'Valami',
            'type': 'miracle',
            'uses': 3,
            'int': 0,
            'fth': 10,
            'graphic': '../graphics/particles/fart5/fart5.png'
        },
    'none': {'name': '', 'graphic': '../graphics/particles/none/64none.png'}
}

# enemy
monster_data = {
    'squid': {'health': 100, 'exp': 100, 'damage': 160, 'magic_damage': 5, 'attack_type': 'slash',
              'magic_type': 'flame',
              'attack_sound': '../audio/attack/slash.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 80,
              'magic_radius': 200,
              'notice_radius': 360, 'drop': 'humanity'},
    'raccoon': {'health': 300, 'exp': 250, 'damage': 40, 'magic_damage': 5, 'attack_type': 'claw', 'magic_type': None,
                'attack_sound': '../audio/attack/claw.wav', 'speed': 4, 'resistance': 1, 'attack_radius': 120,
                'magic_radius': 0,
                'notice_radius': 400, 'drop': 'humanity'},
    'spirit': {'health': 100, 'exp': 110, 'damage': 160, 'magic_damage': 5, 'attack_type': 'thunder',
               'magic_type': None,
               'attack_sound': '../audio/attack/fireball.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 60,
               'magic_radius': 0,
               'notice_radius': 350, 'drop': 'humanity'},
    'bamboo': {'health': 70, 'exp': 120, 'damage': 6, 'magic_damage': 5, 'attack_type': 'leaf_attack',
               'magic_type': None,
               'attack_sound': '../audio/attack/slash.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 50,
               'magic_radius': 0,
               'notice_radius': 300, 'drop': 'humanity'},
    'undead': {'health': 70, 'exp': 120, 'damage': 160, 'magic_damage': 5, 'attack_type': 'leaf_attack',
               'magic_type': None,
               'attack_sound': '../audio/attack/slash.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 50,
               'magic_radius': 0,
               'notice_radius': 300, 'drop': 'humanity'}
}

npc_data = {
    'solaire': {'health': 100, 'exp': 100, 'damage': 160, 'magic_damage': 5, 'attack_type': 'slash',
                'magic_type': 'flame',
                'attack_sound': '../audio/attack/slash.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 80,
                'magic_radius': 200,
                'notice_radius': 360, 'drop': 'humanity'}
}

monster_loot_data = {
    'squid': {'humanity': 1, 'rapier': 1},
    'raccoon': {'humanity': 1, 'rapier': 1},
    'spirit': {'humanity': 1},
    'bamboo': {'rapier': 1},
    'undead': {'rapier': 1}
}