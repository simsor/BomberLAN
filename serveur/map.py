#!/usr/bin/env python2
# coding: utf-8

import pygame
import random

from functions import load_png
from config import ASSET_CAISSE, ASSET_MUR, ASSET_BOMBE, ASSET_FLAME, ASSET_POWER_UP
from config import BOMB_DELAY, BOMB_EXPLOSE_DELAY


HAUT = "haut"
BAS = "bas"
GAUCHE = "gauche"
DROITE = "droite"


def bombeCollide(sprite1, sprite2):
    return sprite2.rect.collidepoint(sprite1.center)


class Bombe(pygame.sprite.Sprite):
    def __init__(self, joueur, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.id = Bombe.calcul_id(self)
        self.joueur = joueur

        self.image, self.rect = load_png(ASSET_BOMBE)
        self.rect.center = (x, y)
        self.time = BOMB_DELAY

    def souffle(self, murs, caisses):
        """ Explosion de la bombe : gère l'explosion """
        portee = {}
        portee[HAUT] = self.calcul_souffle(self.joueur.bombe_range, self.rect, [0, -32], murs, caisses)
        portee[DROITE] = self.calcul_souffle(self.joueur.bombe_range, self.rect, [32, 0], murs, caisses)
        portee[BAS] = self.calcul_souffle(self.joueur.bombe_range, self.rect, [0, 32], murs, caisses)
        portee[GAUCHE] = self.calcul_souffle(self.joueur.bombe_range, self.rect, [-32, 0], murs, caisses)
        return portee

    def calcul_souffle(self, portee, rect, speed, murs, caisses):
        if portee > 0:
            rectangle = rect.move(speed)
            if pygame.sprite.spritecollideany(rectangle, murs, collided=bombeCollide):
                return 0
            elif pygame.sprite.spritecollideany(rectangle, caisses, collided=bombeCollide):
                return 1
            return 1 + self.calcul_souffle(portee - 1, rectangle, speed, murs, caisses)  # Pas de collision
        return 0  # Portée maximale atteinte

    def update(self, serveur):
        """ Mise à jour de la bombe : réduit le timer, celle-ci explose lorsque timer == 0 """
        self.time -= 1
        if self.time == 0:
            souffle = self.souffle(serveur.murs, serveur.caisses)
            flammes = []
            flammes.append(Flamme(self.rect.centerx, self.rect.centery))

            for direction in souffle:
                xAbs, yAbs = self.rect.center
                for i in range(souffle[direction]):
                    if direction == HAUT:
                        yAbs -= 32
                    elif direction == DROITE:
                        xAbs += 32
                    elif direction == BAS:
                        yAbs += 32
                    elif direction == GAUCHE:
                        xAbs -= 32

                    flammes.append(Flamme(xAbs, yAbs))

            serveur.flammes.add(flammes)

            for c in serveur.clients:
                for flamme in flammes:
                    c.Send({'action': 'flamme', 'flamme_center': flamme.rect.center, 'flamme_id': flamme.id})
                c.Send({'action': 'bombe_remove', 'bombe_id': self.id})

            if self.joueur.bombe_number < self.joueur.bombe_max_number:
                self.joueur.bombe_number += 1

            self.kill()

    @staticmethod
    def calcul_id(bombe):
        return id(bombe)


class Flamme(pygame.sprite.Sprite):
    """ Représente une flamme, résultat de l'explosion d'une bombe
    Chaque flamme détruit une caisse ou une joueur
    """

    def __init__(self, xAbs, yAbs):
        pygame.sprite.Sprite.__init__(self)
        self.id = Flamme.calcul_id(self)
        self.rect = load_png(ASSET_FLAME)[1]
        self.rect.center = (xAbs, yAbs)

        self.timer = BOMB_EXPLOSE_DELAY

    def update(self, serveur):
        """ Mise à jour de la flamme : réduit le timer, celle-ci disparaît lorsque timer == 0 """
        self.timer -= 1
        if self.timer == 0:
            for c in serveur.clients:
                c.Send({'action': 'flamme_remove', 'flamme_id': self.id})
            self.kill()

    @staticmethod
    def calcul_id(flamme):
        return id(flamme)


class Mur(pygame.sprite.Sprite):
    """ Représente un mur indestructible """

    def __init__(self, xAbs, Abs):
        pygame.sprite.Sprite.__init__(self)
        self.rect = load_png(ASSET_MUR)[1]
        self.rect.topleft = (xAbs, Abs)


class Caisse(pygame.sprite.Sprite):
    """ Représente une caisse destructible """

    def __init__(self, xAbs, yAbs):
        pygame.sprite.Sprite.__init__(self)
        self.id = Caisse.calcul_id(self)
        self.rect = load_png(ASSET_CAISSE)[1]
        self.rect.topleft = (xAbs, yAbs)

    def update(self, serveur):
        if pygame.sprite.spritecollide(self, serveur.flammes, False):
            print "Une caisse a été détruite"

            if random.randint(1, 10) <= 1:
                rand = random.randint(1, 3)
                if rand == 1:
                    # create power_up_speed
                    power = PowerUpSpeed(self.rect.x, self.rect.y)
                elif rand == 2:
                    # create power_up_flamme
                    power = PowerUpFlamme(self.rect.x, self.rect.y)
                elif rand == 3:
                    # create power_up_shield
                    power = PowerUpShield(self.rect.x, self.rect.y)
                else:
                    # create power_up_bombe
                    power = PowerUpBombe(self.rect.x, self.rect.y)

                for c in serveur.clients:
                    c.Send({'action': 'powerUp', 'powerUp_type': power.type, 'powerUp_id': power.id,
                            'powerUp_center': power.rect.center})

                serveur.power_ups.add(power)

            for c in serveur.clients:
                c.Send({'action': 'caisse_remove', 'caisse_id': self.id})
            serveur.nb_caisses_explosees += 1
            self.kill()


    @staticmethod
    def calcul_id(caisse):
        return id(caisse)


class PowerUp(pygame.sprite.Sprite):
    """ Représente un power up générique """

    def __init__(self, type, xAbs, yAbs):
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        self.id = PowerUp.calcul_id(self)
        self.rect = load_png(ASSET_POWER_UP[type])[1]
        self.rect.topleft = (xAbs, yAbs)

    def die(self, channels):
        for c in channels:
            c.Send({'action': 'powerUp_remove', 'powerUp_id': self.id})
        self.kill()

    @staticmethod
    def calcul_id(powerUp):
        return id(powerUp)


class PowerUpFlamme(PowerUp):
    """ Représente le power up des flammes : agrandit la portée des bombes """

    def __init__(self, xAbs, yAbs):
        super(PowerUpFlamme, self).__init__("flamme", xAbs, yAbs)
        print "Un power_up de flamme vient d'apparaître"

    def effet(self, joueur):
        joueur.bombe_range += 1
        print "J'agrandi la portée des flammes"


class PowerUpSpeed(PowerUp):
    """ Représente le power up de la vitesse : augmente cette dernière """

    def __init__(self, xAbs, yAbs):
        super(PowerUpSpeed, self).__init__("speed", xAbs, yAbs)
        print "Un power_up de vitesse vient d'apparaître"

    def effet(self, joueur):
        joueur.velocity += 1
        print "J'accelère le joueur"


class PowerUpBombe(PowerUp):
    """ Représente le power up de la bombe : augmente le nombre de bombe par personne """

    def __init__(self, xAbs, yAbs):
        super(PowerUpBombe, self).__init__("bombe", xAbs, yAbs)
        print "Un power_up de bombe vient d'apparaître"

    def effet(self, joueur):
        joueur.bombe_max_number += 1
        joueur.bombe_number += 1
        print "J'augmente le nombre de bombes du joueur"

class PowerUpShield(PowerUp):
    """ Représente le power up bouclier : protège d'une explosion """

    def __init__(self, xAbs, yAbs):
        super(PowerUpShield, self).__init__("shield", xAbs, yAbs)
        print "Un power_up de bouclier vient d'apparaître"

    def effet(self, joueur):
        joueur.bouclier = True
        print "Pickup shield !"
