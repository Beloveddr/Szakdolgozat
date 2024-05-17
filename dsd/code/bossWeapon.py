import pygame


class BossWeapon(pygame.sprite.Sprite):
    def __init__(self, boss, groups):
        super().__init__(groups)
        self.boss = boss
        self.sprite_type = 'boss_weapon'
        direction = 'left'  # I want to get the 0.th item after the split

        # graphics
        full_path = f'../graphics/boss_weapons/{boss.weapon}/{direction}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        # placement
        if direction == 'right':
            self.rect = self.image.get_rect(midleft=boss.rect.midright + pygame.math.Vector2(0, 16))
        elif direction == 'left':
            self.rect = self.image.get_rect(midright=boss.rect.midleft + pygame.math.Vector2(0, 16))
        elif direction == 'down':
            self.rect = self.image.get_rect(midtop=boss.rect.midbottom + pygame.math.Vector2(-10, 0))
        else:
            self.rect = self.image.get_rect(midbottom=boss.rect.midtop + pygame.math.Vector2(-10, 0))
