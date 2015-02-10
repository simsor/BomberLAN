# coding: utf-8

from PodSixNet.Connection import connection, ConnectionListener
import sys
import pygame
import os

def load_png(name):
    """Load image and return image object"""
    fullname=os.path.join('.',name)
    try:
        image=pygame.image.load(fullname)
        if image.get_alpha is None:
            image=image.convert()
        else:
            image=image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    
    return image,image.get_rect()


class BomberlanClient(ConnectionListener):
    def __init__(self, ip, port):
        self.running = False
        self.numero = 0 # Le numéro du joueur
        self.Connect((ip, port))

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
        print "Je suis le numéro %d" % (self.numero)
        self.running = True # On ne lance le jeu que quand on a un numéro

    def Loop(self):
        connection.Pump()
        self.Pump()


class Joueur(pygame.sprite.Sprite, ConnectionListener):
    """ Classe "coquille vide" représentant un joueur """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.bas = load_png("assets/joueur_bas.png")[0]
        self.haut = load_png("assets/joueur_haut.png")[0]
        self.droite = load_png("assets/joueur_droite.png")[0]
        self.gauche = pygame.transform.flip(self.droite, True, False)

        self.image, self.rect = self.bas, self.bas.get_rect()

    def Network_joueur(self, data):
        self.rect.center = data['centre']
        if data["direction"] == "bas":
            self.image = self.bas
        elif data["direction"] == "haut":
            self.image = self.haut
        elif data["direction"] == "gauche":
            self.image = self.gauche
        else:
            self.image = self.droite

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
        self.image, self.rect = load_png("assets/caisse.png")

        self.rect.center = (x, y)

class Bombe(pygame.sprite.Sprite):
    """ Représente une bombe déposée par un joueur """

    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png("assets/bombe3.png")

        self.rect.center = (x,y)

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
            self.add(Caisse(caisse[0], Caisse[1]))

class GroupeBomb(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de de bombe qui écoute le réseau"""
    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_bombes(self, data):
        self.empty()
        for bombe in data["bombes"]:
            self.add(Bombe(bombe[0], Bombe[1]))