# coding: utf-8

import pygame
import sys

import config
from reseau import BomberlanClient, GroupeMurs, GroupeCaisses
from joueur import Joueur, GroupeJoueurs


def main_function():
    if len(sys.argv) != 3:
        print "Usage: %s ip port" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    pygame.init()

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    enCours = True
    clock = pygame.time.Clock()

    joueurs = GroupeJoueurs()
    client = BomberlanClient(ip, port, joueurs)
    murs = GroupeMurs()
    caisses = GroupeCaisses()

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
            client.Loop()

            screen.fill((255, 255, 255))
            joueurs.draw(screen)
            murs.draw(screen)
            caisses.draw(screen)
            pygame.display.flip()

        else:
            client.Loop()