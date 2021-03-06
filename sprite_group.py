import pygame as pg
from pygame import surfarray, sprite

class Sprite(pg.sprite.Sprite):
    """  создаём спрайт на основе поверхности """
    def __init__(self, surf,pos=(0,0),type=1):
        super().__init__()
        self.type=type #1-ground 2-worm
        # переменные .image и .rect нужны для Group
        self.image = surf
        self.rect = self.image.get_rect()
        self.rect.topleft=pos
        self.Vx=self.Vy=0
        self.Fx=self.Fy=0
    def get_shift(self,ds,V):
        dV=1
        if ds>0:
                V+=dV
                if V>ds: V=ds
        elif ds<0:
                V-=dV
                if V<ds: V=ds
        else:
            V=0
        return V
    def move(self,x,y):
        dx=x-self.rect.centerx #distance to move for x
        dy=y-self.rect.y  #distance to move for y
        self.Vx=self.get_shift(dx,self.Vx);        self.rect.x +=self.Vx
        self.Vy=self.get_shift(dy,self.Vy);        self.rect.y +=self.Vy
        return  (self.Vx==0 and self.Vy==0)
    def draw(self, surf):
        surf.blit(self.image, self.rect)
    def update(self):
        pass
class StackGroup(pg.sprite.OrderedUpdates):
    """  вертикальный стек"""
    def __init__(self,x,y,dir,*sprites):
        super().__init__(*sprites)
        # координаты начала воды в столбце
        self.x=x
        self.y=y
        #направление стека
        self.dir=dir # True-стек растёт вверх
    # переопределили super.update()
    def update(self):
        y=self.y
        for sp in self.sprites():
            # send target point for move
            if self.dir :
                sp.move( self.x,  y-sp.rect.height+1) #+1 для небольшого наложения спрайтов
                y = sp.rect.y
            else:
                sp.move( self.x, y)
                y=sp.rect.y+sp.rect.height
            sp.update()
