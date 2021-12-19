import pygame as pg
from pygame import surfarray, sprite
from sprite_group import *
from masterslave import *
import numpy as np
from random import randint
from datetime import datetime, timedelta
import time
import sys

import config as cfg
import colors
from button import Button
from game import Game
from text_object import TextObject
import weapon as wp
import sound as s

groups = []

class Player(Master):
    """
    Класс, наследуеиый от Master и ответственный за создание массивов персонажей, их взаимодействие друг с другом и
    землёй
    """
    def __init__(self, master_file, master_size,
                 slave_file, slave_size,
                 pos=(0, 0), slave_number=3):  # pos[0]-ось стека
        super().__init__(master_file, master_size,
                         slave_file, slave_size,
                         pos)
        # верхним элементом ставим надпись.
        self.selected_slave = 0
        self.bad_slaves = []
        self.line_begin = [0, 0]
        self.down_flag = False
        self.stack_group = StackGroup(pos[0], pos[1], False, self.master_sprite)
        for i in range(slave_number):
            self.make_slave((self.pos[0] - self.slave_rect.width / 2,
                             self.pos[1] + cfg.menu_button_h + self.slave_rect.height * i))
        self.can_move = True

    def make_slave(self, pos):
        slave = super().make_slave(pos)
        self.stack_group.add(slave)

    def kill_slave(self, slave):
        """
        функция, обрабатывающая "убийство" червяка и удаление его тела из активной игровой зоны
        slave: объект класса worm
        """
        slave.update_image = True
        slave.selected = False
        slave.lives = 0
        self.bad_slaves.append(slave)
        self.slaves.remove(slave)
        s.dead_worm.play()

    def worms_rnd(self):
        """
        функция распределяет червей по случайно выбранным столбикам, в которые распределена земля
        """
        for sp in self.slaves:
            self.stack_group.remove(sp)
            gr = randint(0, len(groups) - 1)  # случайное число
            while 1:
                size = len(groups[gr])
                # если верхний элемент земля, тогда добавляем туда спрайт
                if size:
                    sprites = groups[gr].sprites()
                    if (sprites[size - 1].type == 1):  # ground
                        groups[gr].add(sp)
                        break  # while
                gr += 1
                if gr > len(groups) - 1:
                    gr = 0
            # для исключения пересечений во время падения в начале
            sp.rect.centerx = groups[gr].x

    def update(self):
        """
        функция считывает нажатия клавиш с клавиатуры, передает ход между персонажами в одной команде и отвечает
        за перемещение червей в игровом пространстве
        """
        event = self.pop_event()
        if event:
            if event[0] == pg.MOUSEBUTTONDOWN:
                self.down_flag = True
            elif event[0] == pg.MOUSEBUTTONUP:
                self.down_flag = False
            elif event[0] == pg.KEYDOWN and self.can_move:
                worm = self.slaves[self.selected_slave]
                i = int(worm.rect.x / cfg.sprite_width) - 1
                if event[1] == pg.K_LEFT:
                    worm.key = False  # left
                    if i:
                        groups[i].remove(worm)
                        groups[i - 1].add(worm)
                        s.walk_left.play()
                elif event[1] == pg.K_RIGHT:
                    worm.key = True  # right
                    if i < len(groups) - 1:
                        groups[i].remove(worm)
                        groups[i + 1].add(worm)
                        s.walk_right.play()
                elif event[1] == pg.K_UP:
                    if (len(self.slaves) > 1):
                        prev = self.selected_slave
                        self.selected_slave = (self.selected_slave + 1) % len(self.slaves)
                        self.slaves[prev].selected = False
                        self.slaves[self.selected_slave].selected = True
                        self.slaves[prev].update_image = True
                        self.slaves[self.selected_slave].update_image = True
                        s.select_worm.play()
                elif event[1] == pg.K_DOWN:
                    if (len(self.slaves) > 1):
                        prev = self.selected_slave
                        num = self.selected_slave - 1
                        if (num < 0):
                            self.selected_slave = len(self.slaves) - 1
                        else:
                            self.selected_slave = num % len(self.slaves)
                        self.slaves[prev].selected = False
                        self.slaves[self.selected_slave].selected = True
                        self.slaves[prev].update_image = True
                        self.slaves[self.selected_slave].update_image = True
                        s.select_worm.play()

    def draw(self, surf):
        #if self.down_flag == True:
        #    pass
        pass

    def set_weapon_default(self, weapon):
        """
        функция устанавливает дефолтное оружие при передаче хода к определенному червю
        weapon: объект класса Weapon
        """
        for i in range(len(self.slaves)):
            self.slaves[i].set_weapon(weapon)

    def set_weapon_active_slave(self, weapon):
        """
        функция выдает выбранное пользователем оружие червю
        weapon: объект класса Weapon
        """
        self.slaves[self.selected_slave].set_weapon(weapon)

    def activate(self, On):
        size = len(self.slaves)
        if size:
            if self.selected_slave >= size:
                self.selected_slave = randint(0, size - 1)
            for i in range(size):
                if i == self.selected_slave:
                    self.slaves[i].selected = On
                else:
                    self.slaves[i].selected = False
                self.slaves[i].update_image = True


class Worm(Game):
    """
    Основной класс программы, наследуемый от класса игры Game, он создает кнопки меню, персонажей игры, за которые
    будут играть пользователи, также отвечает за считывание сигналов нажатия на кнопку выбора оружия
    """
    def __init__(self):
        Game.__init__(self, 'Worms',
                      cfg.screen_width,
                      cfg.screen_height,
                      cfg.background_image,
                      cfg.frame_rate)
        self.lives = cfg.initial_lives
        self.menu_buttons = []  # список кнопок для удаления из Game.objects[]
        self.is_game_running = False
        self.players = []
        self.selected_player = 0
        # рассчитываем количество столбцов
        self.n_col = int(cfg.screen_width / cfg.sprite_width) - 2
        self.water_spr = None
        self.weapons = []
        self.selected_weapon = 0
        self.fire_start = False
        self.time_left = cfg.round_time
        self.start_time = 0
        self.score_text = pg.font.SysFont(cfg.font_name, int(cfg.font_size * 1.5))
        self.create_objects()  # вызов для создания всех объектов игры

    def key_event(self, type, key):
        """
        помещение игрового события в массив обрабатываемых событий
        type: тип нажатой клавиши
        key: ключ события
        """
        self.players[self.selected_player].push_event(type, key)

    def set_gun(self):
        """
        Установка в качестве оружия ружья
        """
        self.selected_weapon = 0

    def set_bomb(self):
        """
        Уствновка в качестве оружия базуки
        """
        self.selected_weapon = 1

    def handle_mouse_event(self, type, pos):
        """
        диспетчер обработки событий нажатия мыши
        """
        for b in self.menu_buttons:
            if b.bounds.collidepoint(pos[0], pos[1]):
                b.handle_mouse_event(type, pos)
                return
        if type in (pg.MOUSEBUTTONDOWN,
                    pg.MOUSEBUTTONUP):
            self.players[self.selected_player].push_event(type, pos)
            if type == pg.MOUSEBUTTONDOWN:
                if (self.is_game_running):
                    self.weapons[self.selected_weapon].get_angle(
                        self.players[self.selected_player].slaves[self.players[self.selected_player].selected_slave],
                        pos[0], pos[1], groups)
            if type == pg.MOUSEBUTTONUP:
                if (self.is_game_running and self.selected_weapon == 1):
                    self.weapons[self.selected_weapon].fire()

    def create_menu(self):
        """
        Создание кнопок меню, находящихся в правом верхнем углу
        """
        def on_play(button):
            """
            обработка нажатия кнопки Play
            """
            if not self.is_game_running:
                self.is_game_running = True
                self.start_level = True
                self.players[0].worms_rnd()
                self.players[1].worms_rnd()
                s.team_drop.play()

        def on_quit(button):
            """
            обработка нажатия кнопки Quit
            """
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
                                                   ('BAZUKA', on_another_gun))):
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


    def create_weapon(self):
        """
        добавление оружия в класс игры
        """
        self.weapons.append(wp.Gun(self.surface))
        self.weapons.append(wp.Bazooka(self.surface))

    def create_player(self, weapon):
        """
        Создание игроков, обозначение их комманд на экране, отрисовка спрайтов разных игроков и добавление в массив
        управляющих кнопок
        """
        master_size = (cfg.menu_button_w * 2, cfg.menu_button_h)
        slave_size = (cfg.sprite_width, cfg.sprite_height)
        for i, (master, slave, x) in enumerate(((cfg.player_image_1, cfg.worm_image_1, 200),
                                                (cfg.player_image_2, cfg.worm_image_2, 600))):
            player = Player(master, master_size,
                            slave, slave_size,
                            (x, cfg.sprite_height), 3)
            self.players.append(player)
            self.objects.append(player)
            self.objects.append(player.stack_group)

        self.players[0].set_weapon_default(weapon)
        self.players[1].set_weapon_default(weapon)

        self.mouse_handlers.append(self.handle_mouse_event)
        self.keydown_handlers[pg.K_LEFT].append(self.key_event)
        self.keydown_handlers[pg.K_RIGHT].append(self.key_event)
        self.keydown_handlers[pg.K_UP].append(self.key_event)
        self.keydown_handlers[pg.K_DOWN].append(self.key_event)

    def create_ground(self):
        """
        создание спрайтов земли и их отображение на экране в случайном порядке для создания карты
        """
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
            groups.append(StackGroup(water_rect.x + i * cfg.sprite_width + cfg.sprite_width / 2,
                                     water_rect.y + 2, True))
            # переносим все группы в self.objects, чтобы класс Game отрисовывал их
            self.objects.append(groups[i])
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
                groups[grp - 1].add(Sprite(ground_surf, (x, y), type=1))
            rows -= 1
            nb -= i + 1
        del rnd

    def create_objects(self):
        """
        функция, вызывающая создание всех объектов игры
        """
        self.create_ground()
        self.create_weapon()
        self.create_player(self.weapons[self.selected_weapon])
        self.players[1].activate(False)
        self.players[0].activate(True)
        self.create_menu()

    def show_message(self, text, color=colors.WHITE, font_name='Arial', font_size=20, centralized=False):
        """
        вывод сообщения text на экран с задержкой игрового процесса на время вывода сообщения
        """
        message = TextObject(cfg.screen_width // 2, cfg.screen_height // 2, lambda: text, color, font_name, font_size)
        self.draw()
        message.draw(self.surface, centralized)
        pg.display.update()
        time.sleep(cfg.message_duration)

    def collide_player_water(self, player):
        """
        обработка взаимодействия червей с водой
        player: игрок, чей червь столкнулся с водой
        """
        dict = pg.sprite.spritecollide(self.water_spr, self.players[player].slaves_group, True, False)
        if len(dict):
            for sp in dict:
                s.splash.play()
                sp.kill()  # удаляем из всех групп
                # переносим в bad_slaves
                self.players[player].kill_slave(sp)
                self.players[player ^ 1].stack_group.add(sp)
                self.start_time = pg.time.get_ticks()
            if player == self.selected_player:
                self.players[player].activate(True)

    def collide_players(self):
        """
        обработка столкновений червей из разных команд;тот кто попал на вражеского червя, отправляется в рай
        """
        slaves = []
        for slave in self.players[self.selected_player ^ 1].slaves_group:
            if slave.lives == 0:
                slaves.append(slave)
                self.players[self.selected_player ^ 1].slaves_group.remove(slave)
        # сравниваем группы и удаляем того, кто напоролся на противника.
        dict = pg.sprite.groupcollide(self.players[self.selected_player].slaves_group,
                                      self.players[self.selected_player ^ 1].slaves_group,
                                      True, False)
        for slave in slaves:
            self.players[self.selected_player ^ 1].slaves_group.add(slave)
        if len(dict):
            for sp in dict:
                sp.kill()  # удаляем из всех групп
                # переносим в bad_slaves
                self.players[self.selected_player].kill_slave(sp)
                # переход хода
                self.players[self.selected_player].activate(False)
                self.selected_player = self.selected_player ^ 1
                self.players[self.selected_player].stack_group.add(sp)
                self.players[self.selected_player].activate(True)
                self.start_time = pg.time.get_ticks()
                s.impact.play()

    def kill_players(self, player):
        """
        берёт список убитых червяков из оружия и обрабатывает его
        player: игрок, чьи черви будут проверяться
        """
        for weapon in self.weapons:
            for worm in weapon.killed_worms:
                dict = pg.sprite.spritecollide(worm, self.players[player].slaves_group, True, False)
                if len(dict):
                    for sp in dict:
                        sp.kill()  # удаляем из всех групп
                        # переносим в bad_slaves
                        self.players[player].kill_slave(sp)
                        self.players[player ^ 1].stack_group.add(sp)
                    if player == self.selected_player:
                        self.players[player].activate(True)

    def block_movement(self):
        """
        не даёт двигаться активному червю, если происходит выстрел, а также передаёт ход после выстрела
        """
        if not self.fire_start:
            for weapon in self.weapons:
                if not weapon.fire_end():
                    self.fire_start = True
                    self.players[self.selected_player].can_move = False
                    break
        if self.fire_start:
            if self.weapons[0].fire_end() and self.weapons[1].fire_end():
                self.fire_start = False
                self.players[self.selected_player].can_move = True
                self.players[self.selected_player].activate(False)
                self.selected_player = self.selected_player ^ 1
                self.players[self.selected_player].activate(True)
                self.start_time = pg.time.get_ticks()

    def weapon_update(self):
        if self.is_game_running:
            self.players[self.selected_player].set_weapon_active_slave(self.weapons[self.selected_weapon])
            self.players[self.selected_player].slaves[
                self.players[self.selected_player].selected_slave].update_image = True

    def timer_update(self):
        """
        показывает время до конца хода, а также передаёт ход по истечении
        """
        if (self.start_time != 0 and not self.fire_start):
            self.time_left = cfg.round_time - int((pg.time.get_ticks() - self.start_time) / 1000)
        textsurface = self.score_text.render('Time:', False, colors.WHITE)
        self.surface.blit(textsurface, (0, 150))
        color = colors.GREEN2
        if (self.time_left <= 5):
            color = colors.RED2
        textsurface1 = self.score_text.render(str(self.time_left), False, color)
        self.surface.blit(textsurface1, (cfg.font_size * 4, 150))
        if (self.time_left == 0):
            self.players[self.selected_player].activate(False)
            self.selected_player = self.selected_player ^ 1
            self.players[self.selected_player].activate(True)
            self.start_time = pg.time.get_ticks()

    def update(self):
        """
        обработка результатов игры
        """
        # выход сразу, если игра не запущена (on_play/on_quit)
        if not self.is_game_running:
            return

        if self.start_time == 0:
            self.start_time = pg.time.get_ticks()

        if self.start_level:
            self.start_level = False
            self.show_message('GET READY!', centralized=True)

        if not len(self.players[0].slaves):
            s.gameover.play()
            self.show_message('PLAYER 2- WINNER!!!', centralized=True)
            self.is_game_running = False  # стоп игра
        #  self.game_over = True
        if not len(self.players[1].slaves):
            s.gameover.play()
            self.show_message('PLAYER 1- WINNER!!!', centralized=True)
            self.is_game_running = False  # стоп игра
        self.weapon_update()
        self.block_movement()
        self.timer_update()
        self.collide_players()  # ищем столкновения между червями разных игроков
        # ищем столкновения между червями разных игроков и водой
        self.collide_player_water(self.selected_player)
        self.collide_player_water(self.selected_player ^ 1)
        self.kill_players(self.selected_player)
        self.kill_players(self.selected_player ^ 1)
        self.weapons[self.selected_weapon].draw(groups)

        super().update()
        if self.game_over:            self.show_message('GAME OVER!', centralized=True)


def main():
    Worm().run()


if __name__ == '__main__':
    main()


