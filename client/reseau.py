# coding: utf-8

import sys
import pygame

from PodSixNet.Connection import connection, ConnectionListener
from joueur import Joueur

from functions import load_png


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


class Mur(pygame.sprite.Sprite):
    """ Représente un mur indestructible """

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png("assets/mur.png")

        self.rect.center = (x, y)


class Caisse(pygame.sprite.Sprite):
    """ Représente une caisse destructible """

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png("assets/caisse_2.png")

        self.rect.center = (x, y)


class Bombe(pygame.sprite.Sprite):
    """ Représente une bombe déposée par un joueur """

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png("assets/bombe3.png")

        self.rect.center = (x, y)


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


class GroupeBombes(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de de bombe qui écoute le réseau"""

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_bombes(self, data):
        self.empty()
        for bombe in data["bombes"]:
            self.add(Bombe(bombe[0], bombe[1]))
