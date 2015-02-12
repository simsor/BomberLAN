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
        self.bombes = pygame.sprite.Group()
        self.flammes = pygame.sprite.Group()

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

        # On crée les caisses : on rempli le centre, en ne laissant que les spawns de libres
        for i in range(3, ARENA_WIDTH - 3, 1):
            self.caisses.add(Caisse(i * 32, 1 * 32))
            self.caisses.add(Caisse(i * 32, (ARENA_HEIGHT - 2) * 32))

        for i in range(3, ARENA_HEIGHT - 3, 1):
            self.caisses.add(Caisse(1 * 32, i * 32))
            self.caisses.add(Caisse((ARENA_WIDTH - 2) * 32, i * 32))

        for i in range(2, ARENA_HEIGHT - 2, 1):
            if i % 2 == 0:
                for j in range(3, ARENA_WIDTH - 3, 2):
                    self.caisses.add(Caisse(j * 32, i * 32))
            else:
                for j in range(2, ARENA_WIDTH - 2, 1):
                    self.caisses.add(Caisse(j * 32, i * 32))

        # On crée les listes de centres de murs et de caisses
        self.centres_murs = [mur.rect.center for mur in self.murs]
        self.centres_caisses = [caisse.rect.center for caisse in self.caisses]

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

    """
    def update_flammes(self):
        # Envoie toutes les flammes à tous les clients
        self.centres_flammes = [(f.rect.centerx, f.rect.centery, f.timer) for f in self.flammes]
        for c in self.channels:
            c.Send({'action': 'flammes', 'flammes': self.centres_flammes})
    """

    def update_caisses(self):
        """ Envoie toutes les caisses à tous les clients """
        self.centres_caisses = [c.rect.center for c in self.caisses]
        for c in self.channels:
            c.Send({'action': 'caisses', 'caisses': self.centres_caisses})

    def main_loop(self):
        """
        Boucle principale du serveur : gère l'envoie et la réception des données principalement
        """
        while True:
            self.clock.tick(60)
            self.Pump()

            # On update les bombes
            self.bombes.update(self)

            # On update les flammes
            self.flammes.update(self)
            """
            nb_flammes = len(self.flammes)
            self.flammes.update()
            if nb_flammes != len(self.flammes):
                self.update_flammes()
            """

            # On update les caisses
            nb_caisses = len(self.caisses)
            self.caisses.update(self.flammes)
            if nb_caisses != len(self.caisses):
                self.update_caisses()

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
