# coding: utf-8

import pygame
import sys

from reseau import BomberlanClient, GroupeMurs, GroupeCaisses, GroupeBombes, GroupeFlammes
from joueur import GroupeJoueurs
from map import Sol, Shadow
from config import SCREEN_WIDTH, SCREEN_HEIGHT, ARENA_HEIGHT, ARENA_WIDTH


def main_function():
    if len(sys.argv) != 3:
        print "Usage: %s ip port" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    pygame.init()

    screen = pygame.display.set_mode((ARENA_WIDTH * 32, ARENA_HEIGHT * 32), pygame.RESIZABLE)
    enCours = True
    clock = pygame.time.Clock()

    joueurs = GroupeJoueurs()
    client = BomberlanClient(ip, port, joueurs)
    murs = GroupeMurs()
    caisses = GroupeCaisses()
    bombes = GroupeBombes()
    flammes = GroupeFlammes()
    background = pygame.sprite.Group()

    for i in range(0, ARENA_WIDTH):
        for j in range(0, ARENA_HEIGHT):
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
            flammes.Pump()
            client.Loop()

            flammes.update()

            screen.fill((255, 255, 255))
            background.draw(screen)

            for j in joueurs:
                xAbs, yAbs = j.rect.midbottom
                shadow = Shadow((xAbs, yAbs - 8))
                screen.blit(shadow.image, shadow.rect)

            murs.draw(screen)
            caisses.draw(screen)
            bombes.draw(screen)
            joueurs.draw(screen)
            flammes.draw(screen)

            pygame.display.flip()

        else:
            client.Loop()