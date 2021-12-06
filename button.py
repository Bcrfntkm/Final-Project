import pygame

from game_object import GameObject
from random import randint
from text_object import TextObject
import config as c
import Sprite
import game


class Button(GameObject):
    def __init__(self, x, y, w, h, text, on_click=lambda x: None, padding=0):
        super().__init__(x, y, w, h)
        self.text = text
        self.button_img = pygame.image.load(c.button_pictures[self.text])
        button_surf = pygame.transform.scale(self.button_img, (15, 15))
        button_rect = button_surf.get_rect(bottomright=(c.screen_width, c.screen_height))
        self.sprite = Sprite.Sprite(button_surf, (x, y))
        self.state = 'normal'
        self.on_click = on_click
        self.groups = []
        """self.text = TextObject(x + padding,
                                           y + padding,
                                            lambda: text,
                                            c.button_text_color,
                                            c.font_name,
                                            c.font_size)"""


    @property
    def back_color(self):
        # цвет в зависимости от состояния кнопки [self.state]
        return dict(normal=c.button_normal_back_color,
                    hover=c.button_hover_back_color,
                    pressed=c.button_pressed_back_color)[self.state]

    def draw(self, surface):
        pygame.draw.rect(surface, self.back_color, self.bounds)
        self.sprite.draw(surface)

    # pygame.MOUSEMOTION
    def handle_mouse_move(self, pos):
        if self.bounds.collidepoint(pos):
            if self.state != 'pressed':
                self.state = 'hover'
        else:
            self.state = 'normal'

    # pygame.MOUSEBUTTONDOWN
    def handle_mouse_down(self, pos):
        if self.bounds.collidepoint(pos):
            self.state = 'pressed'

    # pygame.MOUSEBUTTONUP
    def handle_mouse_up(self, pos):
        if self.state == 'pressed':
            self.on_click(self)
            self.state = 'hover'

    def handle_mouse_event(self, type, pos):
        if type == pygame.MOUSEMOTION:
            self.handle_mouse_move(pos)
        elif type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_down(pos)
        elif type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up(pos)
