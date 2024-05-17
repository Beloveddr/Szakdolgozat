import pygame


class Consumable(pygame.sprite.Sprite):
    def __init__(self, player, groups, item):
        super().__init__(groups)
        self.sprite_type = 'consumable'
        direction = player.status.split('_')[0]  # I want to get the 0.th item after the split

        # graphics
        full_path = f'../graphics/consumables/{item}/{direction}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        # placement
        if direction == 'right':
            self.rect = self.image.get_rect(midleft=player.rect.midright + pygame.math.Vector2(-18, -8))
        elif direction == 'left':
            self.rect = self.image.get_rect(midright=player.rect.midleft + pygame.math.Vector2(14, -8))
        elif direction == 'down':
            self.rect = self.image.get_rect(midtop=player.rect.midbottom + pygame.math.Vector2(-10, -25))
        else:
            self.rect = self.image.get_rect(midbottom=player.rect.midtop + pygame.math.Vector2(-10, 5))
