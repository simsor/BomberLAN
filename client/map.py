# coding: utf-8

import pygame

from functions import load_png
from config import ASSET_SOL, ASSET_JOUEUR


class Sol(pygame.sprite.Sprite):
    """Représente un sol animé"""

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(ASSET_SOL)

        self.rect.center = (x, y)


class Shadow(pygame.sprite.Sprite):
    """Représente une ombre"""

    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(ASSET_JOUEUR['SHADOW'])

        self.rect.center = center
