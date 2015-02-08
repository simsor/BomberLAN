# coding: utf-8

import pygame
import config
import sys
from reseau import BomberlanClient, Joueur, GroupeMurs

def main_function():

    if len(sys.argv) != 3:
        print "Usage: %s ip port" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])
        
    pygame.init()

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    client = BomberlanClient(ip, port)
    enCours = True
    clock = pygame.time.Clock()

    joueur = Joueur(10, 10)
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

            client.Loop()
            joueur.Pump()
            murs.Pump()
            caisses.Pump()
            
            screen.fill((255, 255, 255))
            screen.blit(joueur.image, joueur.rect)
            murs.draw(screen)
            caisses.draw(screen)
            pygame.display.flip()

        else:
            client.Loop()
