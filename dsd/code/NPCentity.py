import pygame
from math import sin
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from settings import TILESIZE


class NPCEntity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2()

        # pathfinding
        self.path = []
        self.grid = Grid(matrix=[])

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0

    def get_collisions(self):
        return self.collision_rects

    def set_matrix(self, value):
        self.grid = Grid(matrix=value)

    # pathfinder
    def empty_path(self):
        self.path = []

    def get_coord(self):
        col = self.rect.centerx // TILESIZE
        row = self.rect.centery // TILESIZE
        return (col, row)

    def set_path(self, path):
        self.path = path
        self.create_collision_rects()
        self.get_direction()

    # create collisions on the way
    def create_collision_rects(self):
        if self.path:
            self.collision_rects = []
            for point in self.path:
                x = (point[0] * TILESIZE) + 32
                y = (point[1] * TILESIZE) + 32
                rect = pygame.Rect((x - 32, y - 32), (64, 64))
                # self.create_lost_souls(str((x, y)))
                self.collision_rects.append(rect)

    def get_direction(self):
        if self.collision_rects:
            # print(self.collision_rects)
            start = pygame.math.Vector2(self.pos)
            end = pygame.math.Vector2(self.collision_rects[0].center)
            if (end - start).length_squared() > 0:
                self.direction = (end - start).normalize()
        else:
            self.direction = pygame.math.Vector2(0, 0)
            self.path = []

    # checking collisions to adjust direction
    def check_collisions(self):
        if self.collision_rects:
            for rect in self.collision_rects:
                if rect.collidepoint(self.pos):
                    del self.collision_rects[0]
                    self.get_direction()
        else:
            self.empty_path()

    def create_path(self, to_spawn=False):
        # start point
        start_x, start_y = self.get_coord()
        start = self.grid.node(start_x, start_y)

        # end point
        if not to_spawn:
            end_x, end_y = self.player_coord()
        else:
            end_x, end_y = self.spawn_pos
        end = self.grid.node(end_x, end_y)

        # path
        pathfinder = AStarFinder()
        self.path, _ = pathfinder.find_path(start, end, self.grid)

        # reset
        self.grid.cleanup()

        self.set_path(self.path)
