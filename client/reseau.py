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
        self.Connect((ip, port))

    def Network_connected(self, data):
        self.running = True
        print "Connecté au serveur !"

    def Network_error(self, data):
        print 'error:', data['error']
        connection.Close()
                
    def Network_disconnected(self, data):
        print 'Server disconnected'
        sys.exit()

    def Loop(self):
        connection.Pump()
        self.Pump()


class Joueur(pygame.sprite.Sprite, ConnectionListener):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.bas = load_png("assets/joueur_bas.png")[0]
        self.haut = load_png("assets/joueur_haut.png")[0]
        self.droite = load_png("assets/joueur_droite.png")[0]
        self.gauche = pygame.transform.flip(self.droite, False, True)

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
