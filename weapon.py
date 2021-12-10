from pygame import surface
import colors
import pygame
from pygame.draw import *
import math
import config as c

class Weapon:
    def __init__(self, surface):
        '''класс оружия будет хранить в себе координаты, которые сначала будут координатами пушки, а потом координатами "пули"
        скорости пули
        цвет (тоже будет для пушки и пули менятся)
        сила заряда выстрела (для ружья не используется)
        угол выстрела'''
        self.surface = surface
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.color = colors.GRAY
        self.f_power = 10
        self.an = 1

        self.tagetting_state = False
        self.fire_state = False

    def power_up(self):
        pass

    def get_angle(self, x, y):
        '''планируется, что будут получаться координаты из прицеливания'''
        self.an = math.atan((self.y-y) / (self.x-x))
        self.tagetting_state = True

    def draw_power_bar(self):
        '''полоска,отображающая силу заряда выстрела (для базуки, например)'''
        width = 10
        coords = [
            (self.x, self.y),
            (self.x+(self.f_power+20)*math.cos(self.an),
             self.y+(self.f_power+20)*math.sin(self.an)),
            (self.x+(self.f_power+20)*math.cos(self.an)+width*math.sin(self.an),
             self.y+(self.f_power+20)*math.sin(self.an)-width*math.cos(self.an)),
            (self.x+width*math.sin(self.an), self.y-width*math.cos(self.an))
        ]
        polygon(self.screen, self.color, (coords), width=0)

    def fire(self):
        '''передаёт скорость в момент выстрела пуле'''
        pass

    def draw(self):
        '''в зависимости от состояния, тут либо отрисовка силы заряда, либо орисовка пули/снаряда'''
        if self.tagetting_state:
            self.draw_power_bar()
        elif self.fire_state:
            self.draw_bullet()
        else:
            pass

    def draw_bullet(self): #рисуетяс пуля, при этом скорости тут же меняются
        pass

    def collision(self, bricks): #проверка столкновения с блоками
        pass
    def on_hit(self, worms): #проверка столкновения с червяком
        pass



class Gun(Weapon):
    def draw_bullet(self):
        width = 1
        coords = [
            (self.x, self.y),
            (self.x+(10)*math.cos(self.an),
             self.y+(10)*math.sin(self.an)),
            (self.x+(10)*math.cos(self.an)+width*math.sin(self.an),
             self.y+(10)*math.sin(self.an)-width*math.cos(self.an)),
            (self.x+width*math.sin(self.an), self.y-width*math.cos(self.an))
        ]
        self.x += self.vx
        self.y += self.vy
        polygon(self.screen, colors.YELLOW1, (coords), width=0)

    def fire(self):
        self.vx = 200 * math.cos(self.an)/2
        self.vy = -200 * self.f_power * math.sin(self.an)/2
        self.f_power = 10
        self.tagetting_state = False
        self.fire_state = True

    def collision(self, bricks):
        if self.x > c.screen_width + 50 or self.x < c.screen_width - 50 or self.y > c.screen_height + 50 or self.y < c.screen_height:
            self.fire_state = False
        else:
            for brick in bricks:
                # FIXME проверка на столкновение с каждым объектом рельефа
                # если будет попадание по кирпичику, то нужен какой-то brick.remove()
                '''
                if brick is on hit:
                    brick.remove()
                    self.fire_state = False
                    break
                '''
                pass
    
    def on_hit(self, worm):
        # FIXME нужно как-то передавать червяков с их координатами и делать проверку на попадание
        return False

    








