# coding: utf-8

import pygame
import sys

import config
from reseau import BomberlanClient, GroupeMurs, GroupeCaisses, GroupeBombes
from joueur import GroupeJoueurs
from functions import load_png


def main_function():
    if len(sys.argv) != 3:
        print "Usage: %s ip port" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    pygame.init()

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
    enCours = True
    clock = pygame.time.Clock()

    joueurs = GroupeJoueurs()
    client = BomberlanClient(ip, port, joueurs)
    murs = GroupeMurs()
    caisses = GroupeCaisses()
    bombes = GroupeBombes()
    background = pygame.sprite.Group()

    for i in range(0, config.ARENA_WIDTH):
        for j in range(0, config.ARENA_HEIGHT):
            background.add(Sol(i * 32, j * 32))

    while enCours:
        clock.tick(60)

        if client.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    enCours = False

            touches = pygame.key.get_pressed()
            client.Send({"action": "keys", "keys": touches})

            joueurs.Pump()
            murs.Pump()
            caisses.Pump()
            bombes.Pump()
            client.Loop()

            screen.fill((255, 255, 255))
            background.draw(screen)
            murs.draw(screen)
            caisses.draw(screen)
            joueurs.draw(screen)
            """
            for j in joueurs:
                shadow = Shadow(j.rect.center)
                screen.blit(shadow.image, shadow.rect)
            """
            bombes.draw(screen)
            pygame.display.flip()

        else:
            client.Loop()


class Sol(pygame.sprite.Sprite):
    """Représente un sol animé"""

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png("assets/bg_1.png")

        self.rect.center = (x, y)


class Shadow(pygame.sprite.Sprite):
    """Représente une ombre"""

    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png("assets/shadow.png")

        self.rect.center = center
