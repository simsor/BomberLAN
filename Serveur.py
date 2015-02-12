#!/usr/bin/env python2
# coding: utf-8

import pygame
import sys

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from config import ARENA_HEIGHT, ARENA_WIDTH
from serveur.map import Mur, Caisse
from serveur.joueur import Joueur


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
