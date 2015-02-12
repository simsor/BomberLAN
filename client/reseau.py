# coding: utf-8

import sys
import pygame

from PodSixNet.Connection import connection, ConnectionListener

from joueur import Joueur
from map import Caisse, Mur, Bombe, Flamme


class BomberlanClient(ConnectionListener):
    def __init__(self, ip, port, groupe_joueurs):
        self.running = False
        self.numero = 0  # Le numéro du joueur
        self.Connect((ip, port))
        self.groupe_joueurs = groupe_joueurs

    def Network_connected(self, data):
        print "Connecté au serveur !"

    def Network_error(self, data):
        print 'error:', data['error']
        connection.Close()

    def Network_disconnected(self, data):
        print 'Server disconnected'
        sys.exit()

    def Network_numero(self, data):
        self.numero = data["numero"]
        print "Je suis le client numéro %d" % (self.numero)
        self.running = True  # On ne lance le jeu que quand on a un numéro
        self.groupe_joueurs.add(Joueur(self.numero))

    def Loop(self):
        connection.Pump()
        self.Pump()


class GroupeMurs(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de murs qui écoute sur le réseau """

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_murs(self, data):
        self.empty()
        for mur in data["murs"]:
            self.add(Mur(mur[0], mur[1]))


class GroupeCaisses(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de caisses qui écoute sur le réseau """

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_caisses(self, data):
        self.empty()
        for caisse in data["caisses"]:
            self.add(Caisse(caisse[0], caisse[1]))


class GroupeFlammes(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de flammes qui écoute sur le réseau """

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_flamme(self, data):
        flamme = data['flamme']
        self.add(Flamme(flamme[0], flamme[1]))

    def Network_flamme_remove(self, data):
        self.flammeByCenter(data['flamme']).kill()

    def flammeByCenter(self, center):
        return [flamme for flamme in self if flamme.rect.center == center][0]


class GroupeBombes(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de bombes qui écoute le réseau"""

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_bombe(self, data):
        bombe = data['bombe']
        self.add(Bombe(bombe[0], bombe[1]))

    def Network_bombe_remove(self, data):
        self.bombeByCenter(data['bombe']).kill()

    def bombeByCenter(self, center):
        return [bombe for bombe in self if bombe.rect.center == center][0]