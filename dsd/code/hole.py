import pygame


class Hole(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player):
        super().__init__(groups)

        # graphic elements
        self.sprite_type = 'invisible'

        self.player = player

        # graphics setup
        self.image = pygame.image.load(f'../graphics/blocks/empty/24x24transparent.png').convert_alpha()

        self.rect = self.image.get_rect(center=pos)

        self.hitbox = self.rect.inflate(-60, -60)

    def update(self):
        if self.player.hitbox.colliderect(self.rect):
            self.player.status = 'falling'
            self.player.vitality = 0
