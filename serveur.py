#!/usr/bin/env python2
# coding: utf-8

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from client import config
import pygame
import sys, os

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


class Joueur(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.bas = load_png("assets/joueur_bas.png")[0]
        self.haut = load_png("assets/joueur_haut.png")[0]
        self.droite = load_png("assets/joueur_droite.png")[0]
        self.gauche = pygame.transform.flip(self.droite, False, True)
        self.direction = "bas"
        
        self.image, self.rect = self.bas, self.bas.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.speed = [0, 0]

    def up(self):
        self.speed[1] = -config.PLAYER_SPEED
        centre = self.rect.center
        self.image, self.rect = self.haut, self.haut.get_rect()
        self.rect.center = centre
        self.direction = "haut"

    def down(self):
        self.speed[1] = config.PLAYER_SPEED
        centre = self.rect.center
        self.image, self.rect = self.bas, self.bas.get_rect()
        self.rect.center = centre
        self.direction = "bas"

    def left(self):
        self.speed[0] = -config.PLAYER_SPEED
        centre = self.rect.center
        self.image, self.rect = self.gauche, self.gauche.get_rect()
        self.rect.center = centre
        self.direction = "gauche"

    def right(self):
        self.speed[0] = config.PLAYER_SPEED
        centre = self.rect.center
        self.image, self.rect = self.droite, self.droite.get_rect()
        self.rect.center = centre
        self.direction = "droite"
        
    def update(self):
        self.rect = self.rect.move(self.speed)
        self.speed = [0, 0]
        

class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.joueur = Joueur(10, 10)
        self.numero = 0

    def Close(self):
        self._server.del_client(self)

    def update(self):
        self.joueur.update()
        
    def Network_keys(self, data):
        touches = data["keys"];
        if touches[pygame.K_UP]:
            self.joueur.up()
        if touches[pygame.K_DOWN]:
            self.joueur.down()
        if touches[pygame.K_LEFT]:
            self.joueur.left()
        if touches[pygame.K_RIGHT]:
            self.joueur.right()


class MyServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        pygame.init()

        self.screen = pygame.display.set_mode((100, 100))
        self.clients = []
        self.clock = pygame.time.Clock()

        print "Serveur en écoute sur le port %d" % (port)

        self.main_loop()

    def Connected(self, channel, addr):
        print "Connexion de %s:%d" % (addr[0], addr[1])
        channel.numero = len(self.clients)
        self.clients.append(channel)

    def del_client(self, channel):
        print "Client déconnecté"
        self.clients.remove(channel)

    def main_loop(self):
        while True:
            self.clock.tick(60)
            self.Pump()

            for c in self.clients:
                c.update()
                c.Send({"action": "joueur", "centre": c.joueur.rect.center, "direction": c.joueur.direction})

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s ip port" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    
    my_server = MyServer(localaddr = (ip, port))
