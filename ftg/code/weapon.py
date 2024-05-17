import pygame


class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, hand, groups):
        super().__init__(groups)
        self.sprite_type = 'weapon'
        direction = player.status.split('_')[0]  # I want to get the 0.th item after the split

        # graphics

        # have to get which hand we are using
        if hand == 'right':
            full_path = f'../graphics/weapons/{player.weapon}/{direction}.png'
        else:
            full_path = f'../graphics/weapons/{player.left_weapon}/{direction}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        # placement
        if direction == 'right':
            # splitting the methods by hand because we have 2
            if hand == 'left':
                self.rect = self.image.get_rect(
                    midleft=player.rect.midright + self.offset_converter(player.left_weapon, True))
            else:
                self.rect = self.image.get_rect(
                    midleft=player.rect.midright + self.offset_converter(player.weapon, True))

        elif direction == 'left':
            # self.rect = self.image.get_rect(midright=player.rect.midleft + pygame.math.Vector2(0, 16))
            if hand == 'left':
                self.rect = self.image.get_rect(
                    midright=player.rect.midleft + self.offset_converter(player.left_weapon, True))
            else:
                self.rect = self.image.get_rect(
                    midright=player.rect.midleft + self.offset_converter(player.weapon, True))
        elif direction == 'down':
            # self.rect = self.image.get_rect(midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
            if hand == 'left':
                self.rect = self.image.get_rect(
                    midtop=player.rect.midbottom + self.offset_converter(player.left_weapon, False))
            else:
                self.rect = self.image.get_rect(
                    midtop=player.rect.midbottom + self.offset_converter(player.weapon, False))
        else:
            # self.rect = self.image.get_rect(midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))
            if hand == 'left':
                self.rect = self.image.get_rect(
                    midbottom=player.rect.midtop + self.offset_converter(player.left_weapon, False, 5))
            else:
                self.rect = self.image.get_rect(
                    midbottom=player.rect.midtop + self.offset_converter(player.weapon, False, 5))

    # switch case method for offsetting different kind of weapons
    def offset_converter(self, weapon, is_x, top=0):
        # splitting the cases because of directions
        # if direction is on the x (left, right) we use a different case than y
        if is_x:
            return {
                'hand_axe': pygame.math.Vector2(0, 26),
                'black_knight_halberd': pygame.math.Vector2(0, 14)
            }.get(weapon, pygame.math.Vector2(0, 16))  # default value
        else:
            # we need the 'top' value if direction == top, because it's not the same as the down direaction
            return {
                'hand_axe': pygame.math.Vector2(-10 + top, 0),
                'black_knight_halberd': pygame.math.Vector2(-14, 0)
            }.get(weapon, pygame.math.Vector2(-10, 0))