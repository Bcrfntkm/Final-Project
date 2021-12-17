import pygame as pg
from SpriteGroup import *
import config as cfg

class Master(): #Player/Weapon
    def __init__(self,master_file,master_size,
                            slave_file,slave_size,
                            pos = (0, 0)):  # pos[0]-ось стека
        self.slave_width=slave_size[0]
        self.slave_height=slave_size[1]
        self.slave_file=slave_file
        self.slaves=[]
        self.selected_slave=0
        self.events = [] #mouse,key
        self.pos=pos

        # загружаем картинку Player
        img = pg.image.load(master_file)
        self.master_surf = pg.transform.scale(img, master_size)
        self.master_rect = self.master_surf.get_rect()

        self.master_rect.centerx = self.pos[0]
        self.master_rect.y = self.pos[1]
        self.master_sprite=Sprite(self.master_surf,
               (self.pos[0] - self.master_rect.width/2,
                self.pos[1] ), type=3)
        # загружаем картинку worm
        img = pg.image.load(slave_file)
        self.slave_surf = pg.transform.scale(img,slave_size)
        self.slave_rect = self.slave_surf.get_rect()

        self.slaves_group = pg.sprite.Group()
    def make_slave(self, pos):
        slave = SlaveWorm(self.slave_surf,pos,type=2)
        self.slaves.append(slave)
        self.slaves_group.add(slave)  # для контроля столкновений
        return slave
    def update(self):
            pass
    def draw(self):
        pass
    def push_event(self, type, par):
        self.events.append((type, par))
    def pop_event(self):
        if len(self.events):
            return self.events.pop(0)
        return False
class SlaveWorm(Sprite):
    def __init__(self,surf,pos=(0,0),type=1):
        super().__init__(surf,pos,type)
        self.weapon=None
        self.lives=cfg.initial_lives
        self.color = (0xFF,0xFF,0xFF)
        self.font = pg.font.SysFont(cfg.font_name,
                                cfg.font_size)
        self.update_image=True
        self.dir=True #спрайт смотрит вправо
        self.key=True #pg.K_RIGHT
        self.image_0=self.image.copy()
        self.selected=False
        self.update()
    # self.stopped=True
    def set_weapon(self,weapon):
        self.weapon=weapon
        self.update_image=True
    def get_surface(self, text):
        text_surface = self.font.render(text, False, self.color)
        return text_surface, text_surface.get_rect()
    def update(self):
        if self.dir!=self.key:
            self.image=pg.transform.flip(self.image,True,False)
            self.image_0=pg.transform.flip(self.image_0,True,False)
#            self.image_0=self.image.copy()
            self.dir=not self.dir
        if self.update_image==True:
            if not self.selected:
                # текст над спрайтом для отображения количества жизней
                self.text_surf, self.bounds = self.get_surface(str(self.lives))
            else:
                self.text_surf = self.weapon.master_surf
                self.bounds=self.text_surf.get_rect()
            self.bounds.centerx = self.rect.width / 2
            self.image=self.image_0.copy()
            self.image.blit(self.text_surf, self.bounds)
        self.update_image = False
    def draw(self,surf):
        surf.blit(self.image,self.rect)
class SlaveBullet(Sprite):
    def __init__(self,surf,pos=(0,0),type=4):
        super().__init__(surf,pos,type)
        self.lives=cfg.initial_lives
        self.color = (0xFF,0xFF,0xFF)
    def update(self):
        pass
    def draw(self,surf):
        surf.blit(self.image,self.rect)
