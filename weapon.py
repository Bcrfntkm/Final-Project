from pygame import surface
import colors
import pygame
from pygame.draw import *
import math
import config as c


'''
Пока от прицеливания не придут координаты прицела, все дествия игнорируются. Класс понимает это через tagetting_state и fire_state
get_angle получает координаты по нажатию кнопки мыши в прицеливании, после чего targetting_state = True (в Gun сразу fire)
Пока кнопка мыши нажата, вызывается draw_power_bar (через draw), но для Gun сразу произойдёт выстрел 
Когда произойдёт выстрел, вызывается fire, и targetting_state = False, fire_state = True
Перемещение пули и отрисовка совмещены в draw_bullet (которая вызывается через draw)
Пока fire_state = True, будет проверка на вылет за пределы экрана и столкновение с кирпичиками и червяками (hit)
При вылете за пределы или попаданию куда либо fire_state = False. Класс снова игнорирует все действия до следующей передачи координат

'''

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


    def get_pos(self, worm):
        self.x = worm.rect.centerx
        self.y = worm.rect.centery

    def get_angle(self, worm, x, y):
        '''планируется, что будут получаться координаты из прицеливания'''
        self.get_pos(worm)
        self.an = math.atan((self.y-y) / (self.x-x))
        self.tagetting_state = True
        

    def draw_power_bar(self):
        '''полоска,отображающая силу заряда выстрела (для базуки, например)'''
        if (self.f_power < 50):
            self.f_power += 1
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

    def draw_bullet(self): #рисуется пуля, при этом скорости тут же меняются
        pass

    def hit(self, bricks, worms): #проверка столкновения с блоками и червяками
        pass



class Gun(Weapon):
    def get_angle(self, x, y):
        '''так как это ружьё, то будет сразу выстрел, а выстрел, вызванный отпусканием мыши, далее проигнорируется'''
        self.an = math.atan((self.y-y) / (self.x-x))
        self.fire()

    def draw_bullet(self):
        width = 3
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
        self.vy -= 0.3 #пока просто тестовое значение
        polygon(self.screen, colors.YELLOW1, (coords), width=0)

    def fire(self):
        if (not self.fire_state):
            self.vx = 200 * math.cos(self.an)/2
            self.vy = -200 * math.sin(self.an)/2
            self.f_power = 10
            self.tagetting_state = False
            self.fire_state = True

    def hit(self, bricks, worms):
        #вылет за экран
        if self.x > c.screen_width + 50 or self.x < c.screen_width - 50 or self.y > c.screen_height + 50 or self.y < c.screen_height:
            self.fire_state = False        
        else:
            #попадание по червяку, отнимает у него одну жизнь
            for worm in worms:
                if (worm.rect.left < self.x < worm.rect.right and worm.rect.top < self.y < worm.rect.bottom):
                    worm.lives -= 1
                    self.fire_state = False
                    return
            #попадание по блоку, убирает блок из списка блоков
            for brick in bricks:
                if (brick.rect.left < self.x < brick.rect.right and brick.rect.top < self.y < brick.rect.bottom):
                    bricks.pop(bricks.index(brick))
                    self.fire_state = False
                    return

class Bazooka(Weapon):
    def __init__(self, surface):
        super().__init__(self, surface)

        #координаты центра передней части снаряда для удобства (см. draw_bullet)
        self.col_x = self.x
        self.col_y = self.y

        self.range = 2500 #радиус поражения в квадрате

    def draw_bullet(self):
        width = 20
        coords = [
            (self.x, self.y),
            (self.x+(50)*math.cos(self.an),
             self.y+(50)*math.sin(self.an)),
            (self.x+(50)*math.cos(self.an)+width*math.sin(self.an),
             self.y+(50)*math.sin(self.an)-width*math.cos(self.an)),
            (self.x+width*math.sin(self.an), self.y-width*math.cos(self.an))
        ]
        self.col_x = (self.x+(50)*math.cos(self.an)+self.x+(50)*math.cos(self.an)+width*math.sin(self.an))/2
        self.col_y = (self.y+(50)*math.sin(self.an)+self.y+(50)*math.sin(self.an)-width*math.cos(self.an))/2
        self.x += self.vx
        self.y += self.vy
        self.an = math.atan(self.vy / self.vx) #не уверен, правильно ли так будет, это для наклона в воздухе
        polygon(self.screen, colors.GREEN, (coords), width=0)

    def fire(self):
        if (not self.fire_state):
            self.vx = self.f_power * math.cos(self.an)/2
            self.vy = - self.f_power * math.sin(self.an)/2
            self.f_power = 10
            self.tagetting_state = False
            self.fire_state = True

    def hit(self, bricks, worms):
        #вылет за экран
        if self.x > c.screen_width + 50 or self.x < c.screen_width - 50 or self.y > c.screen_height + 50 or self.y < c.screen_height:
            self.fire_state = False
        else:
            #попадание по червяку,отнимает жизни у всех червей по близости, а также убирает все блоки по близости из списка блоков
            for worm in worms:
                if (worm.rect.left < self.col_x < worm.rect.right and worm.rect.top < self.col_y < worm.rect.bottom):
                    for close_worm in worms:
                        if close_worm != worm and (worm.rect.centerx - close_worm.rect.centerx)**2 + (worm.rect.centery - close_worm.rect.centery)**2 < self.range:
                            close_worm.lives -=1                        
                    for close_brick in bricks:
                        if (worm.rect.centerx - close_brick.rect.centerx)**2 + (worm.rect.centery - close_brick.rect.centery)**2 < self.range:
                            bricks.pop(bricks.index(close_brick))
                worm.lives -= 1
                self.fire_state = False
                return
            #попадание по блоку, отнимает жизни у всех червей поблизости и убирает все блоки по близости из списка блоков
            for brick in bricks:
                if (brick.rect.left < self.col_x < brick.rect.right and brick.rect.top < self.col_y < brick.rect.bottom):
                    for close_worm in worms:
                        if (brick.rect.centerx - close_worm.rect.centerx)**2 + (brick.rect.centery - close_worm.rect.centery)**2 < self.range:
                            close_worm.lives -=1
                    for close_brick in bricks:
                        if close_brick != brick and (brick.rect.centerx - close_brick.rect.centerx)**2 + (brick.rect.centery - close_brick.rect.centery)**2 < self.range:
                            bricks.pop(bricks.index(close_brick))
                bricks.pop(bricks.index(brick))
                self.fire_state = False
                return        
    








