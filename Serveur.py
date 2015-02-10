#!/usr/bin/env python2
# coding: utf-8

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from client import config
import pygame
import sys, os


def load_png(name):
    """Load image and return image object"""
    fullname = os.path.join('.', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message

    return image, image.get_rect()


class Bombe(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.sprite1 = load_png("assets/bombe1.png")[0]
        self.sprite2 = load_png("assets/bombe2.png")[0]
        self.sprite3 = load_png("assets/bombe3.png")[0]

        self.image, self.rect = self.sprite1, self.sprite1.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.time = config.TIME

    def explose(self):
        if self.image == self.sprite1:
            self.image = self.sprite2
        if self.image == self.sprite2:
            self.image = self.sprite3


    def update(self, serveur):
        self.time -= 1
        # if self.time <= 0:
        #   self.explose()


class Joueur(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.bas = load_png("assets/joueur_bas.png")[0]
        self.haut = load_png("assets/joueur_haut.png")[0]
        self.droite = load_png("assets/joueur_droite.png")[0]
        self.gauche = pygame.transform.flip(self.droite, True, False)
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

    def poseBombe(self, groupeBombe):
        groupeBombe.add(Bombe(self.rect.x, self.rect.y))


    def update(self, serveur):
        ancienCentre = self.rect.center
        self.rect = self.rect.move(self.speed)
        collisions_murs = pygame.sprite.spritecollide(self, serveur.murs, False)
        collisions_caisses = pygame.sprite.spritecollide(self, serveur.caisses, False)
        if collisions_murs or collisions_caisses:
            self.rect.center = ancienCentre
            # On arrondit la position pour qu'il soit aligné
            self.rect.x = 32 * round(self.rect.midtop[0] / 32)
            self.rect.y = 32 * round(self.rect.midright[1] / 32)

        self.speed = [0, 0]


class Mur(pygame.sprite.Sprite):
    """ Représente un mur indestructible """

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png("assets/mur.png")

        self.rect.topleft = (x, y)


class Caisse(pygame.sprite.Sprite):
    """ Représente une caisse destructible """

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png("assets/caisse_2.png")

        self.rect.topleft = (x, y)


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
            self.joueur.poseBombe(self._server.bombes)


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
        for i in range(0, config.ARENA_WIDTH):
            self.murs.add(Mur(i * 32, 0))
            self.murs.add(Mur(i * 32, config.ARENA_HEIGHT * 32 - 32))

        for i in range(1, config.ARENA_HEIGHT):
            self.murs.add(Mur(0, i * 32))
            self.murs.add(Mur(config.ARENA_WIDTH * 32 - 32, i * 32))

        # On crée la grille
        for i in range(1, config.ARENA_WIDTH - 2):
            for j in range(1, config.ARENA_HEIGHT - 2):
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
        while True:
            self.clock.tick(60)
            self.Pump()
            centres_bombes = []
            for bombe in self.bombes:
                centres_bombes.append((bombe.rect.x, bombe.rect.y))
            for c in self.clients:
                c.update()
                c.Send({"action": "bombes", "bombes": centres_bombes})


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s ip port" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    my_server = MyServer(localaddr=(ip, port))
