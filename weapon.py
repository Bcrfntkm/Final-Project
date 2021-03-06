from pygame import surface
import colors
import pygame as pg
from pygame.draw import *
import math
import config as c
import sound as s


class Weapon:
    def __init__(self, surface):
        '''
        основной класс оружия, отвечающий за его отрисовку и взаимодействие

        x, y - положение полоски мощности/снаряда
        vx, vy - скорость снаряда
        f_power - мощность выстрела (базука)
        an - угол
        col_x, col_y - используются вместо x, y в завимости от направления выстрела
        strike_back, shoot_up - направление выстрела
        targetting_state, fire_state - состояния зарядки оружия и полёта снаряда
        active_worm - хранит в себе червя, совершившего выстрел
        killed_worms - хранит червей, которых убило оружие
        '''
        self.surface = surface
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.f_power = 10  
        self.an = 1

        self.col_x = self.x
        self.col_y = self.y

        self.strike_back = False

        self.tagetting_state = False
        self.fire_state = False

        self.active_worm = []
        self.killed_worms = []

        self.shoot_up = True


    def fire_end(self):
        '''
        показывает, завершён ли выстрел
        '''
        if (not self.tagetting_state and not self.fire_state):
            return True
        else:
            return False

    def get_pos(self, worm):
        '''
        берёт координаты червя
        '''
        self.x = worm.rect.centerx
        self.y = worm.rect.centery

    def get_angle(self, worm, x, y, groups):
        '''
        
        '''
        if (self.tagetting_state or self.fire_state):
            return
        self.killed_worms = []
        self.get_pos(worm)
        if (self.x - x > 0):
            self.strike_back = True
        else:
            self.strike_back = False
        if (self.x-x == 0):
            if (self.y - y > 0):
                self.an = - math.pi/2
            else:
                self.an = math.pi/2
        else:
            self.an = math.atan((self.y-y) / (self.x-x))
        
        i = int(self.x / c.sprite_width)
        if (i > 0 and i <= len(groups)):
            g = groups[i - 1]
            sp_list = g.sprites()
            for sp in sp_list:
                if sp.type == 2:
                    if sp.rect.collidepoint(self.x, self.y):
                        self.active_worm.append(sp)
        self.tagetting_state = True
        

    def draw_power_bar(self):
        '''
        отрисовка полоски,отображающей силу заряда выстрела (для базуки, например)
        '''
        if (self.f_power < 50):
            s.rocket_powerup.play()
            self.f_power += 1
        else:
            s.rocket_powerup.stop()
        width = 2
        if (self.strike_back):
            coords = [
                (self.x, self.y),
                (self.x-(self.f_power+2)*math.cos(self.an),
                self.y-(self.f_power+2)*math.sin(self.an)),
                (self.x-(self.f_power+2)*math.cos(self.an)-width*math.sin(self.an),
                self.y-(self.f_power+2)*math.sin(self.an)+width*math.cos(self.an)),
                (self.x-width*math.sin(self.an), self.y+width*math.cos(self.an))
            ]
        else:
            coords = [
                (self.x, self.y),
                (self.x+(self.f_power+2)*math.cos(self.an),
                self.y+(self.f_power+2)*math.sin(self.an)),
                (self.x+(self.f_power+2)*math.cos(self.an)+width*math.sin(self.an),
                self.y+(self.f_power+2)*math.sin(self.an)-width*math.cos(self.an)),
                (self.x+width*math.sin(self.an), self.y-width*math.cos(self.an))
            ]
        polygon(self.surface, colors.RED1, (coords), width=0)

    def fire(self):
        '''
        передаёт скорость в момент выстрела пуле
        '''
        pass

    def draw(self, groups):
        '''
        в зависимости от состояния, тут либо отрисовка силы заряда, либо орисовка пули/снаряда
        '''
        if self.tagetting_state:
            self.draw_power_bar()
        elif self.fire_state:
            self.draw_bullet(groups)
        else:
            pass

    def draw_bullet(self, groups):
        '''
        отрисовка пули, а также проверка на столкновения через hit()
        '''
        pass

    def hit(self, groups):
        '''
        взаимодействие снаряда с блоками и червями
        '''
        pass



class Gun(Weapon):
    def __init__(self, surface):
        '''
        класс ружья

        master_surf - спрайт ружья, отображающийся над червём
        '''
        super().__init__(surface)
        master_size=(int(c.sprite_width),int(c.sprite_height/2))        
        img = pg.image.load(c.gun_image)
        self.master_surf = pg.transform.scale(img, master_size)


    def get_angle(self, worm, x, y, groups):
        '''
        передаёт угол выстрела классу        
        так как это ружьё, то будет сразу выстрел
        '''
        super().get_angle(worm, x, y, groups)
        self.fire()

    def draw_bullet(self, groups):
        '''
        отрисовка пули, а также проверка на столкновения через hit()
        '''
        width = 1
        coords = [
            (self.x, self.y),
            (self.x+(10)*math.cos(self.an),
             self.y+(10)*math.sin(self.an)),
            (self.x+(10)*math.cos(self.an)+width*math.sin(self.an),
             self.y+(10)*math.sin(self.an)-width*math.cos(self.an)),
            (self.x+width*math.sin(self.an), self.y-width*math.cos(self.an))
        ]
        if self.shoot_up:
            self.col_x = self.x
            self.col_y = self.y
        else:
            self.col_x = (self.x+(10)*math.cos(self.an)+self.x+(10)*math.cos(self.an)+width*math.sin(self.an))/2
            self.col_y = (self.y+(10)*math.sin(self.an)+self.y+(10)*math.sin(self.an)-width*math.cos(self.an))/2
        self.x += self.vx
        self.y += self.vy
        polygon(self.surface, colors.YELLOW1, (coords), width=0)
        if (self.fire_state):
            self.hit(groups)

    def fire(self):
        '''
        передаёт скорость в момент выстрела пуле
        '''
        if (not self.fire_state):
            s.gun_fire.play()
            speed = 20
            if (self.strike_back):
                self.vx = -speed * math.cos(self.an)
                self.vy = -speed * math.sin(self.an)
            else:
                self.vx = speed * math.cos(self.an)
                self.vy = speed * math.sin(self.an)
            if self.vy < 0:
                self.shoot_up = True
            else:
                self.shoot_up = False
            self.f_power = 10
            self.tagetting_state = False
            self.fire_state = True

    def hit(self, groups):
        '''
        проверка на вылет за экран
        взаимодействие снаряда с блоками и червями
        '''

        #вылет за экран
        if self.x > c.screen_width + 50 or self.x <  - 50 or self.y > c.screen_height + 50 or self.y < -50:
            self.fire_state = False 
            self.active_worm = []       
        else:
            #попадание по червяку, отнимает у него одну жизнь
            #попадание по блоку, убирает блок из списка блоков
            
            i = int(self.col_x / c.sprite_width)
            if (i > 0 and i <= len(groups)):
                g = groups[i - 1]
                sp_list = g.sprites()
                for sp in sp_list:
                    if sp.rect.collidepoint(self.col_x, self.col_y):
                        if sp.type == 1 or (sp.type == 2 and sp != self.active_worm[0]):
                            if sp.type == 1:
                                g.remove(sp)
                            elif sp.type == 2:
                                sp.lives -= 1
                                if (sp.lives == 0):
                                    self.killed_worms.append(sp)
                                sp.update_image = True
                            self.fire_state = False
                            self.active_worm = []
                            return

class Bazooka(Weapon):
    def __init__(self, surface):
        '''
        класс базуки

        master_surf - спрайт базуки, отображающийся над червём
        range - половина стороны квадрата, в котором происходит взрыв
        flam_idx, flame_length - отвечают за отрисовку "пламени" снаряда
        '''
        super().__init__(surface)

        self.range = 20

        
        master_size=(int(c.sprite_width),int(c.sprite_height/2))
        
        img = pg.image.load(c.gun2_image)
        self.master_surf = pg.transform.scale(img, master_size)

        self.flame_idx = 1
        self.flame_length = 3

        


    def draw_bullet(self, groups):
        '''
        отрисовка снаряда, а также проверка на столкновения через hit()
        '''
        s.rocket_fly.play()
        width = 5
        coords = [
            (self.x, self.y),
            (self.x+(10)*math.cos(self.an),
             self.y+(10)*math.sin(self.an)),
            (self.x+(10)*math.cos(self.an)+width*math.sin(self.an),
             self.y+(10)*math.sin(self.an)-width*math.cos(self.an)),
            (self.x+width*math.sin(self.an), self.y-width*math.cos(self.an))
        ]
        if self.shoot_up:
            self.col_x = self.x
            self.col_y = self.y
        else:
            self.col_x = (self.x+(10)*math.cos(self.an)+self.x+(10)*math.cos(self.an)+width*math.sin(self.an))/2
            self.col_y = (self.y+(10)*math.sin(self.an)+self.y+(10)*math.sin(self.an)-width*math.cos(self.an))/2
        self.x += self.vx
        self.y += self.vy        
        self.vy += 0.03
        self.an = math.atan(self.vy / self.vx)
        polygon(self.surface, colors.GREEN, (coords), width=0)
        self.flame_length += self.flame_idx
        if self.flame_length == 3 or self.flame_length == 6:
            self.flame_idx = - self.flame_idx
        if not self.strike_back:
            coords2 = [
                (self.x, self.y),
                ((self.x+(-self.flame_length)*math.cos(self.an)+self.x+(-self.flame_length)*math.cos(self.an)+width*math.sin(self.an))/2, 
                (self.y+(-self.flame_length)*math.sin(self.an)+self.y+(-self.flame_length)*math.sin(self.an)-width*math.cos(self.an))/2),
                (self.x+width*math.sin(self.an), self.y-width*math.cos(self.an))
            ]
        else:
            coords2 = [
                (self.x+(10)*math.cos(self.an),
                self.y+(10)*math.sin(self.an)),
                ((self.x+(10+self.flame_length)*math.cos(self.an)+self.x+(10+self.flame_length)*math.cos(self.an)+width*math.sin(self.an))/2, 
                (self.y+(10+self.flame_length)*math.sin(self.an)+self.y+(10+self.flame_length)*math.sin(self.an)-width*math.cos(self.an))/2),
                (self.x+(10)*math.cos(self.an)+width*math.sin(self.an),
                self.y+(10)*math.sin(self.an)-width*math.cos(self.an))
            ]
        polygon(self.surface, colors.YELLOW2, (coords2), width=0)
        self.hit(groups)

    def fire(self):
        '''
        передаёт скорость в момент выстрела снаряду
        '''
        if (not self.fire_state):
            s.rocket_powerup.stop()
            if (self.strike_back):
                self.vx = -self.f_power * math.cos(self.an)/10
                self.vy = -self.f_power * math.sin(self.an)/10
            else:
                self.vx = self.f_power * math.cos(self.an)/10
                self.vy = self.f_power * math.sin(self.an)/10
            self.f_power = 10
            if self.vy < 0:
                self.shoot_up = True
            else:
                self.shoot_up = False
            self.tagetting_state = False
            self.fire_state = True
            s.rocket_lauch.play()
    def hit(self, groups):
        '''
        проверка на вылет за экран, кроме верхней границы
        взаимодействие снаряда с блоками и червями
        '''
        #вылет за экран
        if self.x > c.screen_width + 50 or self.x <  - 50 or self.y > c.screen_height + 50:
            self.fire_state = False
            self.active_worm = []
            s.rocket_fly.stop()
        else:
            # прямое попадание снимет червяку 2 жизни, попадание в область взрыва снимет 1 жизнь червяку или уберёт блок
            i = int(self.col_x / c.sprite_width)
            if (i > 0 and i <= len(groups)):
                g = groups[i - 1]
                sp_list = g.sprites()
                for sp in sp_list:
                    if sp.rect.collidepoint(self.col_x, self.col_y):
                        if (sp.type == 1 or sp.type == 2) and (sp != self.active_worm[0] or (self.shoot_up and self.vy > 0)):
                            if sp.type == 2:
                                sp.lives -= 1
                            self.active_worm = []
                            self.fire_state = False
                            x = self.col_x - self.range
                            y = self.col_y - self.range
                            county = 0
                            while(county < 3):
                                countx = 0
                                while(countx < 3):
                                    k = int((x + self.range*countx) / c.sprite_width)
                                    if (k > 0 and k <= len(groups)):
                                        g1 = groups[k - 1]
                                        sp1_list = g1.sprites()
                                        for sp1 in sp1_list:
                                            if sp1.rect.collidepoint(x + self.range*countx, y + self.range*county):
                                                if sp1.type == 1 or sp1.type == 2:
                                                    if sp1.type == 1:
                                                        g1.remove(sp1)
                                                    else:
                                                        if (sp1.lives != 0):
                                                            sp1.lives -= 1
                                                        if (sp1.lives == 0):
                                                            self.killed_worms.append(sp1)
                                                        sp1.update_image = True

                                                    break
                                    countx += 1
                                county += 1
                            s.rocket_fly.stop()
                            s.explosion.play()
                            return       
    








