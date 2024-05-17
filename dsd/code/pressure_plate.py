import pygame

from support import import_folder


class PressurePlate(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player_r, status, cr_trap_arrow):
        super().__init__(groups)

        # graphic elements
        self.sprite_type = 'chest'

        self.player_rect = player_r
        self.create_trap_arrow = cr_trap_arrow

        # graphics setup
        self.frame_index = 0
        self.animation_speed = 0.15
        self.status = status
        self.import_graphics()
        self.image = self.animations[self.status][self.frame_index]

        # full_path = f'../graphics/drop/item/item.png'
        # self.image = pygame.image.load(full_path).convert_alpha()

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, -10)

        self.activated = False

    def import_graphics(self):
        self.animations = {'active': [], 'inactive': []}
        main_path = f'../graphics/trap/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        self.image.set_alpha(255)

    def update(self):
        self.animate()

        if self.player_rect.colliderect(self.rect) and not self.activated:
            self.create_trap_arrow('down', 100, self.rect)
            self.activated = True
            self.status = 'inactive'
