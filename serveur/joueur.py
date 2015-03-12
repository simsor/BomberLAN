#!/usr/bin/env python2
# coding: utf-8

import pygame
import sys

from functions import load_png
from config import ASSET_JOUEUR
from config import PLAYER_SPEED, PLAYER_LIFE_MAX, BOMB_RANGE, SIDE_LENGTH
from map import Bombe


class Joueur(pygame.sprite.Sprite):
    def __init__(self, numero, spawn_topleft):
        pygame.sprite.Sprite.__init__(self)
        self.numero = numero

        self.image, self.rect = load_png(ASSET_JOUEUR['BAS'])
        self.rect.topleft = spawn_topleft
        self.direction = "bas"

        self.is_at_spawn = False
        self.spawn = pygame.Rect(spawn_topleft, (SIDE_LENGTH, SIDE_LENGTH))
        self.life_max = PLAYER_LIFE_MAX
        self.life = PLAYER_LIFE_MAX

        self.bombe_detection = True
        self.bombe_range = BOMB_RANGE
        self.bombe_max_number = 1
        self.bombe_number = 1

        self.velocity = PLAYER_SPEED
        self.speed = [0, 0]

        self.bouclier = False
        self.bouclierEnDestruction = False

    def respawn(self):
        self.rect.topleft = self.spawn.topleft
        self.direction = "bas"
        self.life -= 1

        self.bombe_detection = True
        self.bombe_range = BOMB_RANGE
        self.bombe_max_number = 1
        self.bombe_number = 1
        self.velocity = PLAYER_SPEED
        self.speed = [0, 0]

    def die(self, serveur):
        channel = serveur.channelByNumero(self.numero)
        channel.Send({'action': 'game_over', 'message': 'vous avez perdu'})
        serveur.del_client(channel)
        serveur.check_win()

    def up(self):
        self.speed[1] = -self.velocity
        self.direction = "haut"

    def down(self):
        self.speed[1] = self.velocity
        self.direction = "bas"

    def left(self):
        self.speed[0] = -self.velocity
        self.direction = "gauche"

    def right(self):
        self.speed[0] = self.velocity
        self.direction = "droite"

    def poseBombe(self, groupeBombes, channels):
        if self.bombe_number <= 0:
            return

        bomb_centerx = (SIDE_LENGTH * round(self.rect.centerx / SIDE_LENGTH)) + 16
        bomb_centery = (SIDE_LENGTH * round(self.rect.centery / SIDE_LENGTH)) + 16
        for b in groupeBombes:
            if b.rect.center == (bomb_centerx, bomb_centery):
                return  # Il y a déjà une bombe ici, on annule

        self.bombe_number -= 1
        self.bombe_detection = False

        bombe = Bombe(self, bomb_centerx, bomb_centery)
        groupeBombes.add(bombe)
        for c in channels:
            c.Send(
                {'action': 'bombe', 'bombe_center': bombe.rect.center, 'bombe_id': bombe.id, 'joueur_id': self.numero})

    def update(self, serveur):
        if self.life <= 0:
            print "Le joueur %d vient de mourir" % self.numero
            self.die(serveur)
            return

        collision_flammes = pygame.sprite.spritecollide(self, serveur.flammes, False,
                                                        pygame.sprite.collide_rect_ratio(0.9))
        shieldState = self.checkShield(collision_flammes)

        if not self.isAtSpawn() and collision_flammes:
            if shieldState:
                if self.life > 1:
                    print "Le joueur %d vient d'exploser (mais n'est pas mort, c'est un Chuck Norris)" % self.numero
                self.respawn()

        else:
            ancienCentre = self.rect.center
            self.rect = self.rect.move(self.speed)

            collisions_murs = pygame.sprite.spritecollide(self, serveur.murs, False)
            collisions_caisses = pygame.sprite.spritecollide(self, serveur.caisses, False)
            collisions_bombes = pygame.sprite.spritecollide(self, serveur.bombes, False)

            if collisions_murs or collisions_caisses or (self.bombe_detection and collisions_bombes):
                self.rect.center = ancienCentre
                # On arrondit la position pour qu'il soit aligné
                self.rect.x = SIDE_LENGTH * round(self.rect.midtop[0] / SIDE_LENGTH)
                self.rect.y = SIDE_LENGTH * round(self.rect.midright[1] / SIDE_LENGTH)

            elif not self.bombe_detection and not collisions_bombes:
                self.bombe_detection = True

            else:
                for power_up in pygame.sprite.spritecollide(self, serveur.power_ups, False):
                    power_up.effet(self)
                    power_up.die(serveur.clients)

        self.speed = [0, 0]


    def isAtSpawn(self):
        if self.spawn.topleft == self.rect.topleft:
            self.is_at_spawn = True

        elif self.is_at_spawn:
            if not self.rect.colliderect(self.spawn):
                self.is_at_spawn = False

        return self.is_at_spawn

    def checkShield(self, coll):
        if not self.bouclier:
            return True
        
        if self.bouclier and coll:
            self.bouclierEnDestruction = True
            print "bouclier en train de fondre"
            return False

        if self.bouclierEnDestruction and not coll:
           self.bouclier = False
           self.bouclierEnDestruction = False
           print "bouclier fondu"
           return False
            
