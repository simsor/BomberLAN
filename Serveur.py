#!/usr/bin/env python2
# coding: utf-8

import pygame
import random
import random
import sys

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from config import ARENA_HEIGHT, ARENA_WIDTH, CAISSE_DELAY, CAISSE_NOMBRE_MINI
from serveur.map import Mur, Caisse
from serveur.joueur import Joueur


class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        self._server.del_client(self)

    def update(self):
        self.joueur.update(self._server)
        for client in self._server.clients:
            self.Send({"action": "joueur_position", "numero": client.joueur.numero, "centre": client.joueur.rect.center,
                       "direction": client.joueur.direction, 'life': client.joueur.life})

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
        Server.__init__(self, localaddr=(ip, port))
        pygame.init()

        self.nb_joueurs = nb_joueurs

        self.screen = pygame.display.set_mode((100, 100))
        self.clients = []
        self.clock = pygame.time.Clock()

        self.murs = pygame.sprite.Group()
        self.caisses = pygame.sprite.Group()
        self.bombes = pygame.sprite.Group()
        self.flammes = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()

        print "Serveur en écoute sur le port %d" % port
        print "En attente des %d joueurs .." % nb_joueurs

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
            if random.randint(0, 1) <= .99:
                self.caisses.add(Caisse(i * 32, 1 * 32))
            if random.randint(0, 1) <= .99:
                self.caisses.add(Caisse(i * 32, (ARENA_HEIGHT - 2) * 32))

        for i in range(3, ARENA_HEIGHT - 3, 1):
            if random.randint(0, 1) <= .99:
                self.caisses.add(Caisse(1 * 32, i * 32))
            if random.randint(0, 1) <= .99:
                self.caisses.add(Caisse((ARENA_WIDTH - 2) * 32, i * 32))

        for i in range(2, ARENA_HEIGHT - 2, 1):
            if i % 2 == 0:
                for j in range(3, ARENA_WIDTH - 3, 2):
                    if random.randint(0, 1) <= .99:
                        self.caisses.add(Caisse(j * 32, i * 32))
            else:
                for j in range(2, ARENA_WIDTH - 2, 1):
                    if random.randint(0, 1) <= .99:
                        self.caisses.add(Caisse(j * 32, i * 32))

        # On crée les listes de centres de murs et de caisses
        self.centres_murs = [mur.rect.center for mur in self.murs]

        self.main_loop()

    def Connected(self, channel, addr):
        nb_player = len(self.clients)
        if nb_player >= self.nb_joueurs:
            channel.Send({'action': 'error', 'error': 'impossible de se connecter : le serveur est plein'})
            print "Impossible de connecter \"%s:%d\", le serveur est plein" % (addr[0], addr[1])
            print "Déconnection de \"%s:%d\"" % (addr[0], addr[1])
            return

        print "Bonjour \"%s:%d\" !" % (addr[0], addr[1])

        numeros = [c.joueur.numero for c in self.clients]
        for i in range(4):
            if not numeros.__contains__(i):
                nb_player = i
                break

        xSpawn = (1 + (ARENA_WIDTH - 3) * (nb_player % 2)) * 32
        ySpawn = (1 + (ARENA_HEIGHT - 3) * int(nb_player * 0.6)) * 32
        channel.joueur = Joueur(nb_player, xSpawn, ySpawn)
        channel.Send({"action": "numero", "numero": channel.joueur.numero, 'life': channel.joueur.life})

        # On envoie les murs et les caisses
        channel.Send({"action": "murs", "murs_center": self.centres_murs})

        # On envoie les caisses, bombes, flammes et power-ups
        for caisse in self.caisses:
            channel.Send({'action': 'caisse', 'caisse_center': caisse.rect.center, 'caisse_id': caisse.id})
        for bombe in self.bombes:
            channel.Send({'action': 'bombe', 'bombe_center': bombe.rect.center, 'bombe_id': bombe.id,
                          'joueur_id': bombe.joueur.numero})
        for flamme in self.flammes:
            channel.Send({'action': 'flamme', 'flamme_center': flamme.rect.center, 'flamme_id': flamme.id})
        for powerUp in self.power_ups:
            channel.Send({'action': 'powerUp', 'powerUp_type': powerUp.type, 'powerUp_center': powerUp.rect.center,
                          'powerUp_id': powerUp.id})

        # On envoie les autres joueurs connectés
        for c in self.clients:
            c.Send({"action": "joueur", "numero": channel.joueur.numero, 'life': channel.joueur.life})
            channel.Send({"action": "joueur", "numero": c.joueur.numero, 'life': channel.joueur.life})

        self.clients.append(channel)

        if len(self.clients) == self.nb_joueurs:
            for c in self.clients:
                c.Send({"action": "game_start", "message": "Gooooooooooo !!"})

    def del_client(self, channel):
        if not self.clients.__contains__(channel):
            return

        print "Client %d déconnecté" % (channel.joueur.numero)
        self.clients.remove(channel)
        for c in self.clients:
            c.Send({"action": "joueur_disconnected", "numero": channel.joueur.numero})

    def check_win(self):
        if len(self.clients) == 1:
            print "Victoire du joueur %d ! Bravo (il est très fort !)" % (self.clients[0].joueur.numero)
            self.clients[0].Send({'action': 'game_won', 'message': 'V I C T O I R E  !!'})
            print "FIN DU JEU - plus personne ne veut jouer :'("
            self.running = False


    def channelByNumero(self, numero):
        return [c for c in self.clients if c.joueur.numero == numero][0]


    def randomize_caisse(self):
        toplefts = [m.rect.topleft for m in self.murs]
        toplefts += [c.rect.topleft for c in self.caisses]
        toplefts += [b.rect.topleft for b in self.bombes]
        toplefts += [f.rect.topleft for f in self.flammes]
        toplefts += [p.rect.topleft for p in self.power_ups]
        toplefts += [c.joueur.rect.topleft for c in self.clients]
        toplefts += [c.joueur.spawn for c in self.clients]

        possible_toplefts = []

        for i in range(ARENA_WIDTH):
            for j in range(ARENA_HEIGHT):
                topleft = (i * 32, j * 32)
                if not toplefts.__contains__(topleft):
                    possible_toplefts.append(topleft)

        xAbs, yAbs = possible_toplefts[random.randint(0, len(possible_toplefts) - 1)]
        caisse = Caisse(xAbs, yAbs)
        for c in self.clients:
            c.Send({'action': 'caisse', 'caisse_center': caisse.rect.center, 'caisse_id': caisse.id})

        return caisse


    def main_loop(self):
        """
        Boucle principale du serveur : boucle de jeu
        """
        self.running = True
        self.nb_caisses_explosees = 0
        caisse_timer = CAISSE_DELAY

        while self.running:
            self.clock.tick(60)

            # On update les bombes
            self.bombes.update(self)

            # On update les flammes
            self.flammes.update(self)

            # On update les caisses
            self.caisses.update(self)

            # On envoie toutes les données aux clients
            for c in self.clients:
                c.update()

            if self.nb_caisses_explosees > CAISSE_NOMBRE_MINI:
                caisse_timer -= 1
                if caisse_timer == 0:
                    self.caisses.add(self.randomize_caisse())
                    caisse_timer = CAISSE_DELAY

            self.Pump()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "Usage: %s ip port nb_players" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    nb_joueurs = int(sys.argv[3])

    if nb_joueurs > 4:
        print "BomberLan se joue à 4 joueurs maximum"
        sys.exit(2)

    my_server = MyServer(localaddr=(ip, port), nb_joueurs=nb_joueurs)
