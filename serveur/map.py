#!/usr/bin/env python2
# coding: utf-8

import pygame

from functions import load_png
from config import ASSET_CAISSE, ASSET_MUR, ASSET_BOMBE
from config import BOMB_DELAY, BOMB_RANGE, BOMB_EXPLOSE_DELAY


def bombeCollide(sprite1, sprite2):
    return sprite2.rect.collidepoint((sprite1.x, sprite1.y))


class Bombe(pygame.sprite.Sprite):
    def __init__(self, joueur, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.joueur = joueur

        self.image, self.rect = load_png(ASSET_BOMBE)
        self.rect.x = x
        self.rect.y = y
        self.time = BOMB_DELAY

    def explose(self, murs, caisses):
        """ Explosion de la bombe : gère l'explosion """
        portee = {}
        portee["haut"] = self.chercher(BOMB_RANGE, self.rect, [0, -32], murs, caisses)
        portee["droite"] = self.chercher(BOMB_RANGE, self.rect, [32, 0], murs, caisses)
        portee["bas"] = self.chercher(BOMB_RANGE, self.rect, [0, 32], murs, caisses)
        portee["gauche"] = self.chercher(BOMB_RANGE, self.rect, [-32, 0], murs, caisses)
        return portee

    def chercher(self, portee, rect, speed, murs, caisses):
        if portee > 0:
            rectangle = rect.move(speed)
            if pygame.sprite.spritecollideany(rectangle, murs, collided=bombeCollide) or \
                    pygame.sprite.spritecollideany(rectangle, caisses, collided=bombeCollide):
                return 0
            return 1 + self.chercher(portee - 1, rectangle, speed, murs, caisses)  # Pas de collision
        return 0  # Portée maximale atteinte

    def update(self, serveur):
        """ Mise à jour de la bombe : réduit le timer, celle-ci explose lorsque timer == 0 """
        self.time -= 1
        if self.time == 0:
            deflagration = self.explose(serveur.murs, serveur.caisses)
            for c in serveur.clients:
                c.Send({'action': 'bombe_explose', 'x': self.rect.x, 'y': self.rect.y, 'portee': deflagration})

        if self.time == (-BOMB_EXPLOSE_DELAY):
            for c in serveur.clients:
                c.Send({'action': 'bombe_remove', 'x': self.rect.x, 'y': self.rect.y})
            self.kill()
            return


class Mur(pygame.sprite.Sprite):
    """ Représente un mur indestructible """

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(ASSET_MUR)

        self.rect.topleft = (x, y)


class Caisse(pygame.sprite.Sprite):
    """ Représente une caisse destructible """

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(ASSET_CAISSE)

        self.rect.topleft = (x, y)



