import pygame as pg

class Sprite(pg.sprite.Sprite):
    """  создаём спрайт на основе поверхности """

    def __init__(self, surf, pos=(0, 0), type=1):
        super().__init__()
        # переменные .image и .rect нужны для Group
        self.image = surf
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.Vx = self.Vy = 0
        self.Fx = self.Fy = 0
        # self.stopped=True
        self.type = type  # 1-ground

    def get_shift(self, ds, V):
        dV = 1
        if ds > 0:
            V += dV
            if V > ds: V = ds
        elif ds < 0:
            V -= dV
            if V < ds: V = ds
        else:
            V = 0
        return V

    def move(self, x, y):
        dx = x - self.rect.x  # distance to move for x
        dy = y - self.rect.y  # distance to move for y
        self.Vx = self.get_shift(dx, self.Vx)
        self.rect.x += self.Vx
        self.Vy = self.get_shift(dy, self.Vy)
        self.rect.y += self.Vy
        return (self.Vx == 0 and self.Vy == 0)

    # SpriteBlock.draw(sc)

    def draw(self, surf):
        # на поверхности surf отрисовываем наш image
        surf.blit(self.image, self.rect)

    def update(self, surf):
        pass
