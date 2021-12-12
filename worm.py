import pygame as pg
from pygame import surfarray, sprite
import numpy as np
from random import randint
from datetime import datetime, timedelta
import time
import sys

import config as cfg
import colors
from button import Button
from brick import Brick
from game import Game
from text_object import TextObject



class Sprite(pg.sprite.Sprite):
    """  создаём спрайт на основе поверхности """

    def __init__(self, surf, pos=(0, 0), type=1):
        super().__init__()
        self.type = type  # 1-ground 2-worm
        # переменные .image и .rect нужны для Group
        self.image = surf
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.Vx = self.Vy = 0
        self.Fx = self.Fy = 0

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
        dx = x - self.rect.centerx  # distance to move for x
        dy = y - self.rect.y  # distance to move for y
        self.Vx = self.get_shift(dx, self.Vx);
        self.rect.x += self.Vx
        self.Vy = self.get_shift(dy, self.Vy);
        self.rect.y += self.Vy
        return (self.Vx == 0 and self.Vy == 0)

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    def update(self):
        pass


class Slave(Sprite):
    def __init__(self, surf, pos=(0, 0), type=1):
        super().__init__(surf, pos, type)
        self.weapon = None
        self.lives = cfg.initial_lives
        self.color = 0xFFFFFF
        self.font = pg.font.SysFont(cfg.font_name,
                                    cfg.font_size)
        self.change_weapon = True
        self.image_0 = self.image.copy()
        self.update()

    # self.stopped=True
    def set_weapon(self, weapon):
        self.weapon = weapon
        self.change_weapon = True

    def get_surface(self, text):
        text_surface = self.font.render(text, False, self.color)
        return text_surface, text_surface.get_rect()

    def update(self):
        if self.change_weapon == True:
            if self.weapon == None:
                # текст над спрайтом для отображения количества жизней
                self.text_surf, self.bounds = self.get_surface(str(self.lives))
            else:
                self.text_surf = self.weapon.master_surf
                self.bounds = self.text_surf.get_rect()
            self.bounds.centerx = self.rect.width / 2
            self.image = self.image_0.copy()
            self.image.blit(self.text_surf, self.bounds)
        self.change_weapon = False

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class StackGroup(pg.sprite.OrderedUpdates):
    """  вертикальный стек"""

    def __init__(self, x, y, dir, *sprites):
        super().__init__(*sprites)
        # координаты начала воды в столбце
        self.x = x
        self.y = y
        # направление стека
        self.dir = dir  # True-стек растёт вверх

    # переопределили super.update()
    def update(self):
        y = self.y
        for sp in self.sprites():
            # send target point for move
            if self.dir:
                sp.move(self.x, y - sp.rect.height)
                y = sp.rect.y
            else:
                sp.move(self.x, y)
                y = sp.rect.y + sp.rect.height
            sp.update()


class Master():  # Player/Weapon
    def __init__(self, master_file, master_width, master_height,
                 slave_file, slave_width, slave_height,
                 pos=(0, 0), slave_number=0):  # pos[0]-ось стека
        self.slave_width = slave_width
        self.slave_height = slave_height
        self.slave_file = slave_file
        self.sprites = []
        self.events = []
        self.selected_slave = 0
        self.pos = pos
        # загружаем картинку Player
        img = pg.image.load(master_file)
        self.master_surf = pg.transform.scale(img, (int(master_width), int(master_height)))
        self.master_rect = self.master_surf.get_rect()
        self.master_rect.centerx = self.pos[0]
        self.master_rect.y = self.pos[1]
        self.master_sprite = Sprite(self.master_surf,
                                    (self.pos[0] - self.master_rect.width / 2,
                                     self.pos[1]), type=3)
        # верхним элементом ставим надпись.
        self.group = StackGroup(pos[0], pos[1], False, self.master_sprite)

        for i in range(slave_number):
            self.make_slave(i)
        # и добавляем в группу

    #    self.group.add(self.worms)
    def make_slave(self, i):
        # загружаем картинку worm
        img = pg.image.load(self.slave_file)
        slave_surf = pg.transform.scale(img, (int(self.slave_width), int(self.slave_height)))
        slave_rect = slave_surf.get_rect()
        # на основе картинки создаём спрайты
        self.sprites.append(Slave(slave_surf,
                                  (self.pos[0] - slave_rect.width / 2,
                                   self.pos[1] + cfg.menu_button_h + slave_rect.height * i),
                                  type=2))

    def kill_sprite(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class Weapon(Master):
    def __init__(self, master_file, master_width, master_height,
                 slave_file, slave_width, slave_height,
                 pos=(0, 0), slave_number=0):  # pos[0]-ось стека
        super().__init__(master_file, master_width, master_height,
                         slave_file, slave_width, slave_height)


class Player(Master):
    def __init__(self, master_file, master_width, master_height,
                 slave_file, slave_width, slave_height,
                 pos=(0, 0), slave_number=3):  # pos[0]-ось стека
        super().__init__(master_file, master_width, master_height,
                         slave_file, slave_width, slave_height,
                         pos, slave_number)
        self.selected_slave = 0

    def worms_rnd(self, groups):
        for sp in self.sprites:
            gr = randint(0, len(groups) - 1)  # случайное число
            while 1:
                size = len(groups[gr])
                # если верхний элемент земля, тогда добавляем туда спрайт
                if size:
                    sprites = groups[gr].sprites()
                    if (sprites[size - 1].type == 1):  # ground
                        groups[gr].add(sp)
                        break
                gr += 1
                if gr > len(groups):
                    gr = 0

    def push_event(self, type, par):
        self.events.append((type, par))

    def pop_event(self):
        if len(self.events):
            return self.events.pop(0)
        return False

    def update(self, n_col, groups):
        event = self.pop_event()
        if event:
            if event[0] == pg.MOUSEBUTTONDOWN:
                pos = event[1]
                i = int(pos[0] / cfg.sprite_width)
                if (i > 0 and i <= n_col):
                    g = groups[i - 1]
                    sp_list = g.sprites()
                    for sp in sp_list:
                        if sp.type == 1:
                            if sp.rect.collidepoint(pos[0], pos[1]):
                                g.remove(sp)
                                break
            elif event[0] == pg.KEYDOWN:
                worm = self.sprites[self.selected_slave]
                i = int(worm.rect.x / cfg.sprite_width) - 1
                if event[1] == pg.K_LEFT:
                    if i:
                        groups[i].remove(worm)
                        groups[i - 1].add(worm)
                elif event[1] == pg.K_RIGHT:
                    if i < (n_col - 1):
                        groups[i].remove(worm)
                        groups[i + 1].add(worm)

    def set_weapon_active_slave(self, weapon):
        for i in range(len(self.sprites)):
            if i == self.selected_slave:
                self.sprites[i].set_weapon(weapon)
            else:
                self.sprites[i].set_weapon(None)


"""class PlayerOld():
    обработка действий пользователя    

    def __init__(self, player_file,
                 worm_file,
                 pos=(0, 0)):  # pos[0]-ось стека
        self.events = []
        self.worms = []
        self.selected_worm = 0
        # загружаем картинку Player
        img = pg.image.load(player_file)
        self.player_surf = pg.transform.scale(img, (cfg.menu_button_w * 2,
                                                    cfg.menu_button_h))
        self.player_rect = self.player_surf.get_rect()
        self.player_rect.centerx = pos[0]
        self.player_rect.y = pos[1]
        self.player_sprite = Sprite(self.player_surf,
                                    (pos[0] - self.player_rect.width / 2,
                                     pos[1]), type=3)
        # верхним элементом ставим надпись.
        self.group = StackGroup(pos[0], pos[1], False, self.player_sprite)
        # загружаем картинку worm
        img = pg.image.load(worm_file)
        worm_surf = pg.transform.scale(img, (cfg.sprite_width,
                                             cfg.sprite_width * 2))
        worm_rect = worm_surf.get_rect()
        # на основе картинки создаём спрайты
        for i in range(cfg.initial_lives):
            # self.worms.append(Sprite(worm_surf,
            #                          (pos[0]-worm_rect.width/2,
            #                           pos[1]+cfg.menu_button_h+worm_rect.height*i),
            #                          type=2))
            self.worms.append(Slave(worm_surf,
                                    (pos[0] - worm_rect.width / 2,
                                     pos[1] + cfg.menu_button_h + worm_rect.height * i),
                                    type=2))
        # и добавляем в группу

    #    self.group.add(self.worms)
    def worms_rnd(self, groups):
        for sp in self.worms:
            gr = randint(0, len(groups) - 1)  # случайное число
            while 1:
                size = len(groups[gr])
                # если верхний элемент земля, тогда добавляем туда спрайт
                if size:
                    sprites = groups[gr].sprites()
                    if (sprites[size - 1].type == 1):  # ground
                        groups[gr].add(sp)
                        break
                gr += 1
                if gr > len(groups):
                    gr = 0


# ---------------------------------------breakout"""


class Worm(Game):
    def __init__(self):
        Game.__init__(self, 'Worms',
                      cfg.screen_width,
                      cfg.screen_height,
                      cfg.background_image,
                      cfg.frame_rate)
        self.sound_effects = {name: pg.mixer.Sound(sound) for name, sound in cfg.sounds_effects.items()}
        self.lives = cfg.initial_lives
        # self.reset_effect = None
        # self.effect_start_time = None
        # self.score = 0
        # self.start_level = False
        # self.paddle = None
        # self.bricks = None
        # self.ball = None
        # self.points_per_brick = 1
        self.menu_buttons = []  # список кнопок для удаления из Game.objects[]
        self.is_game_running = False
        self.groups = []  # хранилище групп
        self.players = []
        self.selected_player_0 = True
        # рассчитываем количество столбцов
        self.n_col = int(cfg.screen_width / cfg.sprite_width) - 2
        self.water_spr = None
        self.weapons = []
        self.selected_weapon = 0
        self.create_objects()  # вызов для создания всех объектов игры

    def key_event(self, type, key):
        if self.selected_player_0:
            i = 0
        else:
            i = 1
        self.players[i].push_event(type, key)

    def handle_mouse_event(self, type, pos):
        if type == pg.MOUSEBUTTONDOWN:
            if self.selected_player_0:
                i = 0
            else:
                i = 1
            self.players[i].push_event(type, pos)

    def set_gun(self):
        if self.selected_player_0 == True:
            self.players[0].set_weapon_active_slave(self.gun)
            self.players[1].set_weapon_active_slave(None)
        else:
            self.players[1].set_weapon_active_slave(self.gun)
            self.players[0].set_weapon_active_slave(None)

    def set_bomb(self):
        if self.selected_player_0 == True:
            self.players[0].set_weapon_active_slave(self.gun2)
            self.players[1].set_weapon_active_slave(None)
        else:
            self.players[1].set_weapon_active_slave(self.gun2)
            self.players[0].set_weapon_active_slave(None)

    def create_menu(self):
        def on_play(button):
            # нажата левая кнопка мыши на кнопке Play
            # при запуске игры удаляем все кнопки из отрисовки.
            #           for b in self.menu_buttons:
            #               self.objects.remove(b)
            self.is_game_running = True
            self.start_level = True

            for pl in range(len(self.players)):
                pass
                # if pl == self.selected_player:
                #     self.players[self.selected_player].set_weapon(self.weapons[self.selected_weapon])
                # else:
                #     self.players[self.selected_player].set_weapon()

        #            self.players[self.selected_player].set_worm(True)
        #           player.set_worm(True)
        #           player.set_worm(False)

        def on_quit(button):
            # нажата левая кнопка мыши на кнопке Quit
            self.game_over = True
            self.is_game_running = False

        def on_gun(button):
            self.set_gun()

        def on_another_gun(button):
            self.set_bomb()

        # перебираем перечисление и формируем кнопки с вертикальным расположением
        for i, (text, click_handler) in enumerate((('PLAY', on_play),
                                                   ('QUIT', on_quit),
                                                   ('GUN', on_gun),
                                                   ('ANOTHER GUN', on_another_gun))):
            b = Button(cfg.menu_offset_x,
                       cfg.menu_offset_y + (cfg.menu_button_h + 5) * i,
                       cfg.menu_button_w,
                       cfg.menu_button_h,
                       text,
                       click_handler,
                       padding=5)
            # складируем в self.objects
            self.objects.append(b)  # Game.objects[]
            self.menu_buttons.append(b)  # память объектов - кнопок
            self.mouse_handlers.append(b.handle_mouse_event)  # Game.mouse_handlers[]

    def create_weapon(self):
        self.gun = Weapon(cfg.gun_image, cfg.sprite_width, cfg.sprite_height / 2,
                          cfg.bullet_image, cfg.sprite_width / 2, cfg.sprite_height / 2)
        self.gun2 = Weapon(cfg.gun2_image, cfg.sprite_width, cfg.sprite_height / 2,
                           cfg.bullet2_image, cfg.sprite_width / 2, cfg.sprite_height / 2)
        self.players[0].set_weapon_active_slave(self.gun)
        self.players[1].set_weapon_active_slave(None)

    def create_player(self):
        player = Player(cfg.player_image_1, cfg.menu_button_w * 2, cfg.menu_button_h,
                        cfg.worm_image_1, cfg.sprite_width, cfg.sprite_width * 1.5,
                        (200, cfg.sprite_height), 3)
        player.worms_rnd(self.groups)
        self.players.append(player)
        self.objects.append(player.group)

        player = Player(cfg.player_image_2, cfg.menu_button_w * 2, cfg.menu_button_h,
                        cfg.worm_image_2, cfg.sprite_width, int(cfg.sprite_width * 1.5),
                        (600, cfg.sprite_height), 3)
        #        player= Player(cfg.player_image_2,cfg.worm_image_2,(600,cfg.sprite_height))
        player.worms_rnd(self.groups)
        self.players.append(player)
        self.objects.append(player.group)

        self.mouse_handlers.append(self.handle_mouse_event)
        self.keydown_handlers[pg.K_LEFT].append(self.key_event)
        self.keydown_handlers[pg.K_RIGHT].append(self.key_event)

    def create_ground(self):
        # загружаем образец грунта
        ground_img = pg.image.load(cfg.ground_image)
        ground_surf = pg.transform.scale(ground_img, (cfg.sprite_width, cfg.sprite_height))
        ground_rect = ground_surf.get_rect()
        # создаём sprite "вода" (прямоугольник, поверхность, спрайт)
        water_rect = pg.Rect(cfg.sprite_width,
                             cfg.screen_height - 2 * cfg.sprite_height,
                             cfg.sprite_width * self.n_col,
                             cfg.sprite_height)
        water_surf = pg.Surface(water_rect.size)
        water_surf.fill((100, 150, 200))
        self.water_spr = Sprite(water_surf, (cfg.sprite_width, cfg.screen_height - 2 * cfg.sprite_height))
        self.objects.append(self.water_spr)
        # создаём группы по количеству столбцов
        for i in range(self.n_col):
            self.groups.append(StackGroup(water_rect.x + i * cfg.sprite_width + cfg.sprite_width / 2,
                                          water_rect.y + 2, True))
            # переносим все группы в self.objects, чтобы класс Game отрисовывал их
            self.objects.append(self.groups[i])
        # генерируем в случайном порядке блоки и раскладываем их по группам.
        rows = 6
        nb = self.n_col * 3
        rnd = []  # защита от совпадений
        while nb:
            y = (rows + 1) * cfg.sprite_height * 2 + cfg.sprite_height * 6  # координата y
            rnd.clear()
            for i in range(round(nb / rows)):
                grp = randint(1, self.n_col)  # случайное число
                while grp in rnd:
                    grp += 1
                    if grp > self.n_col:
                        grp = 1
                rnd.append(grp)
                x = grp * cfg.sprite_width  # координата x
                self.groups[grp - 1].add(Sprite(ground_surf, (x, y), type=1))
            rows -= 1
            nb -= i + 1
        del rnd

    def create_objects(self):
        # self.create_bricks()
        # self.create_paddle()
        # self.create_ball()
        # self.create_labels()
        self.create_ground()
        self.create_player()
        self.create_menu()
        self.create_weapon()

    def add_life(self):
        self.lives += 1

    def set_points_per_brick(self, points):
        self.points_per_brick = points

    def change_ball_speed(self, dy):
        self.ball.speed = (self.ball.speed[0], self.ball.speed[1] + dy)

    def show_message(self, text, color=colors.WHITE, font_name='Arial', font_size=20, centralized=False):
        message = TextObject(cfg.screen_width // 2, cfg.screen_height // 2, lambda: text, color, font_name, font_size)
        self.draw()
        message.draw(self.surface, centralized)
        pg.display.update()
        time.sleep(cfg.message_duration)

    # update Worm then Game
    def update(self):
        # выход сразу, если игра не запущена (on_play/on_quit)
        if not self.is_game_running:         return

        if self.start_level:
            self.start_level = False
            self.show_message('GET READY!', centralized=True)

        self.players[0].update(self.n_col, self.groups)
        self.players[1].update(self.n_col, self.groups)
        super().update()
        if self.game_over:            self.show_message('GAME OVER!', centralized=True)


def main():
    Worm().run()


if __name__ == '__main__':
    main()

# pg.init()
# sc = pg.display.set_mode((c.screen_width,
#                                           c.screen_height))
# while 1:
#     for i in pg.event.get():
#         if i.type == pg.QUIT:
#             sys.exit()
#     # рисуем все блоки
#     sc.fill((0x8003B8))
#     sc.blit(water_surf, water_rect)
#     # в каждой группе перебираем все спрайты и сдвигаем, если нужно
#     for i in groups:
#         i.shift_down()
#         i.draw(sc)
#     pg.display.update()
#
#     pg.time.delay(20)
# pg.quit()
