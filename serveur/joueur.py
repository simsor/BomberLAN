#!/usr/bin/env python2
# coding: utf-8

import pygame

from functions import load_png
from config import ASSET_JOUEUR
from config import PLAYER_SPEED

from map import Bombe


class Joueur(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_png(ASSET_JOUEUR['BAS'])
        self.rect.topleft = (x, y)
        self.direction = "bas"

        self.speed = [0, 0]

    def up(self):
        self.speed[1] = -PLAYER_SPEED
        self.direction = "haut"

    def down(self):
        self.speed[1] = PLAYER_SPEED
        self.direction = "bas"

    def left(self):
        self.speed[0] = -PLAYER_SPEED
        self.direction = "gauche"

    def right(self):
        self.speed[0] = PLAYER_SPEED
        self.direction = "droite"

    def poseBombe(self, groupeBombe, channels):
        bomb_x = (32 * round(self.rect.centerx / 32)) + 16
        bomb_y = (32 * round(self.rect.centery / 32)) + 16
        bombe_center = (bomb_x, bomb_y)
        for b in groupeBombe:
            if b.rect.center == bombe_center:
                return  # Il y a déjà une bombe ici, on annule

            if b.joueur == self:
                return  # Il a déjà posé une bombe

        groupeBombe.add(Bombe(self, bombe_center[0], bombe_center[1]))
        for c in channels:
            c.Send({'action': 'bombe', 'bombe': bombe_center})

    def update(self, serveur):
        ancienCentre = self.rect.center
        self.rect = self.rect.move(self.speed)
        collisions_murs = pygame.sprite.spritecollide(self, serveur.murs, False)
        collisions_caisses = pygame.sprite.spritecollide(self, serveur.caisses, False)
        if collisions_murs or collisions_caisses:
            self.rect.center = ancienCentre
            # On arrondit la position pour qu'il soit aligné
            self.rect.x = 32 * round(self.rect.midtop[0] / 32)
            self.rect.y = 32 * round(self.rect.midright[1] / 32)

        if pygame.sprite.spritecollide(self, serveur.flammes, False, pygame.sprite.collide_rect_ratio(0.9)):
            self.rect.topleft = (32, 32)
            print "Un joueur vient de mourir"

        self.speed = [0, 0]
