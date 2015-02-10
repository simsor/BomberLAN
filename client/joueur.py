# coding: utf-8

import pygame

from PodSixNet.Connection import ConnectionListener
from functions import load_png


class Joueur(pygame.sprite.Sprite):
    """ Classe "coquille vide" représentant un joueur """

    def __init__(self, numero):
        pygame.sprite.Sprite.__init__(self)
        self.numero = numero

        self.bas = load_png("assets/joueur_bas.png")[0]
        self.haut = load_png("assets/joueur_haut.png")[0]
        self.droite = load_png("assets/joueur_droite.png")[0]
        self.gauche = pygame.transform.flip(self.droite, True, False)

        self.image, self.rect = self.bas, self.bas.get_rect()

    def updateDirection(self, direction):
        if direction == "bas":
            self.image = self.bas
        elif direction == "haut":
            self.image = self.haut
        elif direction == "gauche":
            self.image = self.gauche
        else:
            self.image = self.droite


class GroupeJoueurs(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de joueurs qui écoute sur le réseau """

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_joueur_position(self, data):
        joueur = self.joueurByNumero(data["numero"])
        joueur.rect.center = data['centre']
        joueur.updateDirection(data["direction"])

    def Network_joueur(self, data):
        print "Connection du joueur %d" % (data["numero"])
        self.add(Joueur(data["numero"]))

    def joueurByNumero(self, numero):
        for joueur in self:
            if joueur.numero == numero:
                return joueur
