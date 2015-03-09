# coding: utf-8

import pygame

from PodSixNet.Connection import ConnectionListener

from functions import load_png
from config import ASSET_JOUEUR, ASSET_ENNEMI

class Joueur(pygame.sprite.Sprite):
    """ Classe "coquille vide" représentant un joueur """

    numeroJoueur = -1

    def __init__(self, numero, life):
        pygame.sprite.Sprite.__init__(self),
        self.numero = numero
        self.life = life

        if numero == Joueur.numeroJoueur:
            # Alors c'est nous
            self.bas = load_png(ASSET_JOUEUR['BAS'])[0]
            self.haut = load_png(ASSET_JOUEUR['HAUT'])[0]
            self.droite = load_png(ASSET_JOUEUR['DROITE'])[0]
            self.gauche = pygame.transform.flip(self.droite, True, False)
        else:
            # C'est un ennemi
            self.bas = load_png(ASSET_ENNEMI['BAS'])[0]
            self.haut = load_png(ASSET_ENNEMI['HAUT'])[0]
            self.droite = load_png(ASSET_ENNEMI['DROITE'])[0]
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
        joueur.life = data['life']
        joueur.rect.center = data['centre']
        joueur.updateDirection(data["direction"])
        joueur.bouclier = data["bouclier"]

    def Network_joueur(self, data):
        print "Connection du joueur %d" % (data["numero"])
        self.add(Joueur(data["numero"], data['life']))

    def Network_joueur_disconnected(self, data):
        print "Deconnection du joueur %d" % (data["numero"])
        self.joueurByNumero(data["numero"]).kill()

    def joueurByNumero(self, numero):
        return [j for j in self if j.numero == numero][0]
