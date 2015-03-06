# coding: utf-8

import pygame

from functions import load_png
from config import ASSET_BOMBE, ASSET_CAISSE, ASSET_MUR
from config import ASSET_SOL, ASSET_JOUEUR, ASSET_POWER_UP
from config import ASSET_FLAME, ASSET_ANIMATE_FLAMES, BOMB_EXPLOSE_DELAY


class Bombe(pygame.sprite.Sprite):
    """ Représente une bombe déposée par un joueur """

    def __init__(self, id, center, joueur_id):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.joueur_id = joueur_id
        self.image, self.rect = load_png(ASSET_BOMBE)

        self.rect.center = center


class Flamme(pygame.sprite.Sprite):
    """ Représente une caisse destructible """

    def __init__(self, id, center):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.image, self.rect = load_png(ASSET_FLAME)

        self.rect.center = center
        self.timer = BOMB_EXPLOSE_DELAY
        self.image_time = BOMB_EXPLOSE_DELAY / len(ASSET_ANIMATE_FLAMES)

    def update(self):
        self.timer -= 1
        for i in range(len(ASSET_ANIMATE_FLAMES)):
            if self.timer == self.image_time * i:
                self.image = load_png(ASSET_ANIMATE_FLAMES[i])[0]
                break


class Sol(pygame.sprite.Sprite):
    """Représente un sol animé"""

    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(ASSET_SOL)

        self.rect.center = center


class Shadow(pygame.sprite.Sprite):
    """Représente une ombre"""

    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(ASSET_JOUEUR['SHADOW'])

        self.rect.center = center


class Mur(pygame.sprite.Sprite):
    """ Représente un mur indestructible """

    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(ASSET_MUR)

        self.rect.center = center


class Caisse(pygame.sprite.Sprite):
    """ Représente une caisse destructible """

    def __init__(self, id, center):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(ASSET_CAISSE)

        self.id = id
        self.rect.center = center


class PowerUp(pygame.sprite.Sprite):
    """ Représente un power up générique """

    def __init__(self, type, id, center):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(ASSET_POWER_UP[type])

        self.id = id
        self.rect.center = center


class PowerUpFlamme(PowerUp):
    """ Représente le power up des flammes : agrandit la portée des bombes """

    def __init__(self, id, center):
        super(PowerUpFlamme, self).__init__("flamme", id, center)


class PowerUpSpeed(PowerUp):
    """ Représente le power up de la vitesse : augmente cette dernière """

    def __init__(self, id, center):
        super(PowerUpSpeed, self).__init__("speed", id, center)


class PowerUpBombe(PowerUp):
    """ Représente le power up de la bombe : augmente le nombre de bombe par personne """

    def __init__(self, id, center):
        super(PowerUpBombe, self).__init__("bombe", id, center)