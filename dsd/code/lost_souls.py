import pygame

from support import import_folder


class Lost_souls(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)

        # graphic elements
        self.sprite_type = 'lost_souls'

        # graphics setup
        self.frame_index = 0
        self.animation_speed = 0.15
        self.import_graphics()
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]

        # full_path = f'../graphics/drop/item/item.png'
        # self.image = pygame.image.load(full_path).convert_alpha()

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, -10)

        # data
        self.health = 1

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 600

    def get_isset(self):
        return False

    def import_graphics(self):
        self.animations = {'idle': []}
        main_path = f'../graphics/drop/lost_souls_animation/'
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
