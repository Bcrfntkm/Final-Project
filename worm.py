import pygame as pg
from pygame import surfarray, sprite
from pygame.rect import Rect
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

    def update(self):
        pass


class StackGroup(pg.sprite.OrderedUpdates):
    """  вертикальный стек"""

    def __init__(self, x, y):
        super().__init__()
        # координаты начала воды в столбце
        self.x = x
        self.y = y

    # переопределили super.update()
    def update(self):
        y = self.y
        for sp in self.sprites():
            # send target point for move
            sp.move(self.x,
                    y - cfg.sprite_height)
            y = sp.rect.y


class Player():
    """обработка действий пользователя    """

    def __init__(self, worm):
        self.worm = worm  # sprite
        self.player_events = []

    def pop_event(self):
        if len(self.player_events):
            return self.player_events.pop(0)
        return False

    def key_event(self, type, key):
        self.player_events.append((type, key))

    def handle_mouse_event(self, type, pos):
        if type == pg.MOUSEBUTTONDOWN:
            self.player_events.append((type, pos))

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
                i = int(self.worm.rect.x / cfg.sprite_width) - 1
                if event[1] == pg.K_LEFT:
                    if i:
                        groups[i].remove(self.worm)
                        groups[i - 1].add(self.worm)
                elif event[1] == pg.K_RIGHT:
                    if i < (n_col - 1):
                        groups[i].remove(self.worm)
                        groups[i + 1].add(self.worm)


class Worm(Game):
    def __init__(self):
        Game.__init__(self, 'Worms',
                      cfg.screen_width,
                      cfg.screen_height,
                      cfg.background_image,
                      cfg.frame_rate)
        self.sound_effects = {name: pg.mixer.Sound(sound) for name, sound in cfg.sounds_effects.items()}
        self.reset_effect = None
        self.effect_start_time = None
        self.score = 0
        self.lives = cfg.initial_lives
        self.start_level = False
        self.paddle = None
        self.bricks = None
        self.ball = None
        self.menu_buttons = []  # список кнопок для удаления из Game.objects[]
        self.is_game_running = False
        self.points_per_brick = 1
        self.groups = []  # хранилище групп
        self.player = None
        # рассчитываем количество столбцов
        self.n_col = int(cfg.screen_width / cfg.sprite_width) - 2
        self.water_spr = None
        self.create_objects()  # вызов для создания всех объектов игры

    def create_menu(self):
        def on_play(button):
            self.is_game_running = True
            self.start_level = True

        def on_quit(button):
            self.game_over = True
            self.is_game_running = False

        def on_gun(button):
            pass  # FIXME передает определенный вид оружия конкретному червю

        def on_another_gun(button):
            pass  # FIXME передает другой вид оружия тому же червю

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

    def create_player(self):
        # загружаем образец червяка
        worm_img = pg.image.load(cfg.worm_image)
        worm_surf = pg.transform.scale(worm_img, (cfg.sprite_width, cfg.sprite_height))
        worm_rect = worm_surf.get_rect()
        # создаём червяка
        y = 1 * cfg.sprite_height * 2  # координата y
        gr = randint(1, self.n_col)  # случайное число
        x = gr * cfg.sprite_width  # координата x

        self.player = Player(Sprite(worm_surf, (x, y), type=2))
        self.mouse_handlers.append(self.player.handle_mouse_event)
        self.groups[gr - 1].add(self.player.worm)

        self.keydown_handlers[pg.K_LEFT].append(self.player.key_event)
        self.keydown_handlers[pg.K_RIGHT].append(self.player.key_event)

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
            self.groups.append(StackGroup(water_rect.x + i * cfg.sprite_width,
                                          water_rect.y))
            # переносим все группы в self.objects, чтобы класс Game отрисовывал их
            self.objects.append(self.groups[i])
        # генерируем в случайном порядке блоки и раскладываем их по группам.
        rows = 6
        nb = self.n_col * 3
        rnd = []  # защита от совпадений
        while nb:
            y = (rows + 1) * cfg.sprite_height * 2  # координата y
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

    def add_life(self):
        self.lives += 1

    # def set_points_per_brick(self, points):  self.points_per_brick = points
    # def change_ball_speed(self, dy):          self.ball.speed = (self.ball.speed[0], self.ball.speed[1] + dy)

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

        # Game.objects[].update
        self.player.update(self.n_col, self.groups)
        super().update()
        if self.game_over:            self.show_message('GAME OVER!', centralized=True)


def main():
    Worm().run()


if __name__ == '__main__':
    main()
