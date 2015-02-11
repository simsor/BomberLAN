#!/usr/bin/env python2
# coding: utf-8

import pygame
import sys

from pprint import pprint

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from functions import load_png
from config import ASSET_JOUEUR, ASSET_CAISSE, ASSET_MUR, ASSET_BOMBE
from config import ARENA_HEIGHT, ARENA_WIDTH, BOMB_DELAY, PLAYER_SPEED, BOMB_RANGE, BOMB_EXPLOSE_DELAY


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
            pprint(deflagration)
            for c in serveur.clients:
                c.Send({'action': 'bombe_explose', 'x': self.rect.x, 'y': self.rect.y, 'portee': deflagration})

        if self.time == (-BOMB_EXPLOSE_DELAY):
            for c in serveur.clients:
                c.Send({'action': 'bombe_remove', 'x': self.rect.x, 'y': self.rect.y})
            self.kill()
            print "bombe removed"


class Joueur(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_png(ASSET_JOUEUR['BAS'])
        self.rect.x = x
        self.rect.y = y
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
        bombx = (32 * round(self.rect.centerx / 32)) + 16
        bomby = (32 * round(self.rect.centery / 32)) + 16
        for b in groupeBombe:
            if b.rect.x == bombx and b.rect.y == bomby:
                return  # Il y a déjà une bombe ici, on annule

            if b.joueur == self:
                return  # Il a déjà posé une bombe

        bombe = Bombe(self, bombx, bomby)
        groupeBombe.add(bombe)
        for c in channels:
            c.Send({'action': 'bombe', 'bombe': (bombe.rect.x, bombe.rect.y)})

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

        self.speed = [0, 0]


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


class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.joueur = Joueur(32, 32)
        self.numero = 0

    def Close(self):
        self._server.del_client(self)

    def update(self):
        self.joueur.update(self._server)
        for client in self._server.clients:
            self.Send({"action": "joueur_position", "numero": client.numero, "centre": client.joueur.rect.center,
                       "direction": client.joueur.direction})

    def Network_keys(self, data):
        touches = data["keys"]
        if touches[pygame.K_UP]:
            self.joueur.up()
        if touches[pygame.K_DOWN]:
            self.joueur.down()
        if touches[pygame.K_LEFT]:
            self.joueur.left()
        if touches[pygame.K_RIGHT]:
            self.joueur.right()
        if touches[pygame.K_SPACE]:
            self.joueur.poseBombe(self._server.bombes, self._server.clients)


class MyServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        pygame.init()

        self.screen = pygame.display.set_mode((100, 100))
        self.clients = []
        self.clock = pygame.time.Clock()

        self.murs = pygame.sprite.Group()
        self.caisses = pygame.sprite.Group()
        self.caisses.add(Caisse(3 * 32, 1 * 32))
        self.caisses.add(Caisse(10 * 32, 5 * 32))
        self.bombes = pygame.sprite.Group()

        print "Serveur en écoute sur le port %d" % (port)

        # On crée une bordure de murs
        for i in range(0, ARENA_WIDTH):
            self.murs.add(Mur(i * 32, 0))
            self.murs.add(Mur(i * 32, ARENA_HEIGHT * 32 - 32))

        for i in range(1, ARENA_HEIGHT):
            self.murs.add(Mur(0, i * 32))
            self.murs.add(Mur(ARENA_WIDTH * 32 - 32, i * 32))

        # On crée la grille
        for i in range(1, ARENA_WIDTH - 2):
            for j in range(1, ARENA_HEIGHT - 2):
                if i % 2 == 0 and j % 2 == 0:
                    self.murs.add(Mur(i * 32, j * 32))

        # On crée les listes de centres de murs et de caisses
        self.centres_murs = []
        for mur in self.murs:
            self.centres_murs.append(mur.rect.center)

        self.centres_caisses = []
        for caisse in self.caisses:
            self.centres_caisses.append(caisse.rect.center)

        self.main_loop()

    def Connected(self, channel, addr):
        print "Connexion de %s:%d" % (addr[0], addr[1])
        channel.numero = len(self.clients)
        channel.Send({"action": "numero", "numero": channel.numero})

        # On envoie les murs et les caisses
        channel.Send({"action": "murs", "murs": self.centres_murs})
        channel.Send({"action": "caisses", "caisses": self.centres_caisses})

        # On envoie les autres joueurs connectés
        for c in self.clients:
            c.Send({"action": "joueur", "numero": channel.numero})
            channel.Send({"action": "joueur", "numero": c.numero})

        self.clients.append(channel)

    def del_client(self, channel):
        print "Client déconnecté"
        self.clients.remove(channel)

    def main_loop(self):
        """
        Boucle principale du serveur : gère l'envoie et la réception des données principalement
        """
        while True:
            self.clock.tick(60)
            self.Pump()

            # On update les bombes
            self.bombes.update(self)

            # On envoie toutes les données aux clients
            for c in self.clients:
                c.update()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s ip port" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    my_server = MyServer(localaddr=(ip, port))
