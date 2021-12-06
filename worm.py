import pygame as pg
from pygame import surfarray, sprite
import numpy as np
from random import randint
from button import Button
import config as c
import Sprite
import button
import colors
from game import Game
from text_object import TextObject
from datetime import datetime, timedelta
import time
# import os
import sys

# размер блока в пикселах
side = 15




class StackGroup(pg.sprite.OrderedUpdates):
    """  вертикальный стек"""

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

    def shift_down(self):
        global side
        y = self.y
        for i in self.sprites():
            # send target point for move
            i.move(i.rect.x, y - side)
            y = i.rect.y
            pass
        pass


# ---------------------------------------breakout
class Worm(Game):
    def __init__(self):
        Game.__init__(self, 'Worms',
                      c.screen_width,
                      c.screen_height,
                      c.background_image,
                      c.frame_rate)
        self.sound_effects = {name: pg.mixer.Sound(sound) for name, sound in c.sounds_effects.items()}
        self.reset_effect = None
        self.effect_start_time = None
        self.score = 0
        self.lives = c.initial_lives
        self.start_level = False
        self.paddle = None
        self.bricks = None
        self.ball = None
        self.menu_buttons = []  # список кнопок
        self.is_game_running = False
        self.create_objects()  # вызов для создания всех объектов игры
        self.points_per_brick = 1

    def create_menu(self):
        def on_play(button):
            # при запуске игры удаляем все кнопки? нет
            #for b in self.menu_buttons:
            #    self.objects.remove(b)
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
            b = Button(c.menu_offset_x,
                       c.menu_offset_y + (c.menu_button_h + 5) * i,
                       c.menu_button_w,
                       c.menu_button_h,
                       text,
                       click_handler,
                       padding=5)
            # складируем в self.objects
            self.objects.append(b)
            self.menu_buttons.append(b)
            self.mouse_handlers.append(b.handle_mouse_event)

    def create_ground(self):
        # загружаем образец грунта
        ground_img = pg.image.load('ground.png')
        ground_surf = pg.transform.scale(ground_img, (15, 15))
        ground_rect = ground_surf.get_rect(bottomright=(c.screen_width, c.screen_height))

        # загружаем образец червяка
        worm_img = pg.image.load('worm.png')
        worm_surf = pg.transform.scale(worm_img, (15, 15))
        worm_rect = worm_surf.get_rect(bottomright=(c.screen_width, c.screen_height))

        # рассчитываем количество столбцов
        n_col = int(c.screen_width / side) - 2
        # создаём sprite "вода" (прямоугольник, поверхность, спрайт)
        water_rect = pg.Rect(side, c.screen_height - 2 * side, side * n_col, side)
        water_surf = pg.Surface(water_rect.size)
        water_surf.fill((100, 150, 200))
        # water_spr=SpriteBlock(water_surf,(side,H-2*side))
        #        sc.blit(water_surf, water_rect)
        # создаём группы по количеству столбцов
        for i in range(n_col):
            self.groups.append(StackGroup(water_rect.x, water_rect.y))
        # генерируем в случайном порядке блоки и раскладываем их по группам.
        rows = 6
        nb = n_col * 3
        rnd = []  # защита от совпадений
        while nb:
            y = (rows + 1) * side * 2  # координата y
            rnd.clear()
            for i in range(round(nb / rows)):
                grp = randint(1, n_col)  # случайное число
                while grp in rnd:
                    grp += 1
                    if grp > n_col:
                        grp = 1
                rnd.append(grp)
                x = grp * side  # координата x
                self.groups[grp - 1].add(Sprite.Sprite(ground_surf, (x, y), type=1))
            rows -= 1
            nb -= i + 1
        del rnd
        # создаём червяка
        y = 1 * side * 2  # координата y
        grp = randint(1, n_col)  # случайное число
        x = grp * side  # координата x
        self.groups[grp - 1].add(Sprite.Sprite(worm_surf, (x, y), type=2))

    def create_objects(self):
        self.create_ground()
        self.create_menu()

    def add_life(self):
        self.lives += 1

    def set_points_per_brick(self, points):
        self.points_per_brick = points

    def change_ball_speed(self, dy):
        self.ball.speed = (self.ball.speed[0], self.ball.speed[1] + dy)

    def handle_ball_collisions(self):
        def intersect(obj, ball):
            edges = dict(left=Rect(obj.left, obj.top, 1, obj.height),
                         right=Rect(obj.right, obj.top, 1, obj.height),
                         top=Rect(obj.left, obj.top, obj.width, 1),
                         bottom=Rect(obj.left, obj.bottom, obj.width, 1))
            collisions = set(edge for edge, rect in edges.items() if ball.bounds.colliderect(rect))
            if not collisions:
                return None

            if len(collisions) == 1:
                return list(collisions)[0]

            if 'top' in collisions:
                if ball.centery >= obj.top:
                    return 'top'
                if ball.centerx < obj.left:
                    return 'left'
                else:
                    return 'right'

            if 'bottom' in collisions:
                if ball.centery >= obj.bottom:
                    return 'bottom'
                if ball.centerx < obj.left:
                    return 'left'
                else:
                    return 'right'

        # Hit paddle
        s = self.ball.speed
        edge = intersect(self.paddle, self.ball)
        if edge is not None:
            self.sound_effects['paddle_hit'].play()
        if edge == 'top':
            speed_x = s[0]
            speed_y = -s[1]
            if self.paddle.moving_left:
                speed_x -= 1
            elif self.paddle.moving_left:
                speed_x += 1
            self.ball.speed = speed_x, speed_y
        elif edge in ('left', 'right'):
            self.ball.speed = (-s[0], s[1])

        # Hit floor
        if self.ball.top > c.screen_height:
            self.lives -= 1
            if self.lives == 0:
                self.game_over = True
            else:
                self.create_ball()

        # Hit ceiling
        if self.ball.top < 0:
            self.ball.speed = (s[0], -s[1])

        # Hit wall
        if self.ball.left < 0 or self.ball.right > c.screen_width:
            self.ball.speed = (-s[0], s[1])

        # Hit brick
        for brick in self.bricks:
            edge = intersect(brick, self.ball)
            if not edge:
                continue

            self.sound_effects['brick_hit'].play()
            self.bricks.remove(brick)
            self.objects.remove(brick)
            self.score += self.points_per_brick

            if edge in ('top', 'bottom'):
                self.ball.speed = (s[0], -s[1])
            else:
                self.ball.speed = (-s[0], s[1])

            if brick.special_effect is not None:
                # Reset previous effect if any
                if self.reset_effect is not None:
                    self.reset_effect(self)

                # Trigger special effect
                self.effect_start_time = datetime.now()
                brick.special_effect[0](self)
                # Set current reset effect function
                self.reset_effect = brick.special_effect[1]

    def show_message(self, text, color=colors.WHITE, font_name='Arial', font_size=20, centralized=False):
        message = TextObject(c.screen_width // 2, c.screen_height // 2, lambda: text, color, font_name, font_size)
        self.draw()
        message.draw(self.surface, centralized)
        pg.display.update()
        time.sleep(c.message_duration)

    # update Worm then Game
    def update(self):
        # выход сразу, если игра не запущена (on_play/on_quit)
        if not self.is_game_running:         return

        if self.start_level:
            self.start_level = False
            self.show_message('GET READY!', centralized=True)

        super().update()
        # рисуем все блоки
        for i in self.groups:
            i.draw(self.surface)

        if self.game_over:
            self.show_message('GAME OVER!', centralized=True)


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
