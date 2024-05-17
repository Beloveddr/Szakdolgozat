UI_BG_COLOR = '#222222'
UI_HUMANITY_ACTIVE_COLOR = '#666666'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'
UI_BORDER_COLOR_ACTIVE = 'gold'

WIDTH = 1280
HEIGTH = 720

CREATOR_BOX_X = 100
CREATOR_BOX_Y = 50

UI_FONT = '../graphics/font/joystix.ttf'
UI_FONT_SIZE = 18
UI_SMALLER_FONT_SIZE = 12
UI_BIGGER_FONT_SIZE = 32

SELECTION_COOLDOWN_TIME = 135
SELECTION_COOLDOWN_TIME_CH = 190

VALID_INPUT_LIST = ['_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                    't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

CLASS_LIST = ['Warrior', 'Knight', 'Wanderer', 'Thief', 'Bandit', 'Hunter', 'Sorcerer', 'Pyromancer', 'Cleric',
              'Deprived']
WARRIOR = {
    "Level": 4,
    "Vitality": 11,
    "Attunement": 8,
    "Endurance": 12,
    "Strength": 13,
    "Dexterity": 13,
    "Inteligence": 9
}
KNIGHT = {
    "Level": 5,
    "Vitality": 14,
    "Attunement": 10,
    "Endurance": 10,
    "Strength": 11,
    "Dexterity": 11,
    "Inteligence": 9
}
WANDERER = {
    "Level": 3,
    "Vitality": 10,
    "Attunement": 11,
    "Endurance": 10,
    "Strength": 10,
    "Dexterity": 14,
    "Inteligence": 11
}
THIEF = {
    "Level": 5,
    "Vitality": 9,
    "Attunement": 11,
    "Endurance": 9,
    "Strength": 9,
    "Dexterity": 15,
    "Inteligence": 12
}
BANDIT = {
    "Level": 4,
    "Vitality": 12,
    "Attunement": 8,
    "Endurance": 14,
    "Strength": 14,
    "Dexterity": 9,
    "Inteligence": 8
}
HUNTER = {
    "Level": 4,
    "Vitality": 11,
    "Attunement": 9,
    "Endurance": 11,
    "Strength": 12,
    "Dexterity": 14,
    "Inteligence": 9
}
SORCERER = {
    "Level": 3,
    "Vitality": 8,
    "Attunement": 15,
    "Endurance": 8,
    "Strength": 9,
    "Dexterity": 11,
    "Inteligence": 15
}
PYROMANCER = {
    "Level": 1,
    "Vitality": 10,
    "Attunement": 12,
    "Endurance": 11,
    "Strength": 12,
    "Dexterity": 9,
    "Inteligence": 10
}
CLERIC = {
    "Level": 2,
    "Vitality": 11,
    "Attunement": 11,
    "Endurance": 9,
    "Strength": 12,
    "Dexterity": 8,
    "Inteligence": 8
}
DEPRIVED = {
    "Level": 6,
    "Vitality": 11,
    "Attunement": 11,
    "Endurance": 11,
    "Strength": 11,
    "Dexterity": 11,
    "Inteligence": 11
}

CLASS_DESCRIPTIONS = ['Weapon expert, high/strength and/dexterity',
                      'High HP, solid/armour, not easily/toppled.',
                      'Wields scimitar,/high dexterity',
                      'High critial hits,/has the Master/Key',
                      'High strength,/wields heavy/battle axe',
                      'Wields bow, weak/with magic and decent/at close range',
                      'Casts soul sorceries',
                      'Casts fire spells/and wields/a hand axe',
                      'Wields a mace and/casts healing/miracles',
                      'Unclothed, only/armed with club and/old shield']
CLASS_ID = {
    'Warrior': 0,
    'Knight': 1,
    'Wanderer': 2,
    'Thief': 3,
    'Bandit': 4,
    'Hunter': 5,
    'Sorcerer': 6,
    'Pyromancer': 7,
    'Cleric': 8,
    'Deprived': 9
}
CLASS_DICT = [WARRIOR, KNIGHT, WANDERER, THIEF, BANDIT, HUNTER, SORCERER, PYROMANCER, CLERIC, DEPRIVED]

GIFT_LIST = ["None", "Goddess's Blessing", "Black Firebomb", "Twin humanities", "Pendant", "Master Key",
             "Tiny Being's Ring", "Old Witch's Ring"]
GIFT_DESCRIPTIONS = [
    "No sign of a gift.",
    "Divine holy water./Fully restores HP/and status.",
    "Explodes upon/impact when thrown.",
    "Tiny sprite called/humanity.",
    "Trinket. No effect,/but fond memories/comfort travelers.",
    "Opens any basic/lock. Initial equip/for thief.",
    "Special tribal/ring. HP recovers/while equipped.",
    "Gift from a witch./Ancient ring with/no obvious effect."
]

STATS_DICT = {
    0: '{"vitality": 11, "attunement": 8, "endurance": 12, "strength": 13, "dexterity": 13, "inteligence": 9, "speed": 5}',
    1: '{"vitality": 14, "attunement": 10, "endurance": 10, "strength": 11, "dexterity": 11, "inteligence": 9, "speed": 5}',
    2: '{"vitality": 10, "attunement": 11, "endurance": 10, "strength": 10, "dexterity": 14, "inteligence": 11, "speed": 5}',
    3: '{"vitality": 9, "attunement": 11, "endurance": 9, "strength": 9, "dexterity": 15, "inteligence": 12, "speed": 5}',
    4: '{"vitality": 12, "attunement": 8, "endurance": 14, "strength": 14, "dexterity": 9, "inteligence": 8, "speed": 5}',
    5: '{"vitality": 11, "attunement": 9, "endurance": 11, "strength": 12, "dexterity": 14, "inteligence": 9, "speed": 5}',
    6: '{"vitality": 8, "attunement": 15, "endurance": 8, "strength": 9, "dexterity": 11, "inteligence": 15, "speed": 5}',
    7: '{"vitality": 10, "attunement": 12, "endurance": 11, "strength": 12, "dexterity": 9, "inteligence": 12, "speed": 5}',
    9: '{"vitality": 11, "attunement": 11, "endurance": 9, "strength": 12, "dexterity": 8, "inteligence": 8, "speed": 5}',
    10: '{"vitality": 11, "attunement": 11, "endurance": 11, "strength": 11, "dexterity": 11, "inteligence": 11, "speed": 5}'
}