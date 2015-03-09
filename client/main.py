# coding: utf-8

import pygame
import time
import sys

from reseau import BomberlanClient, GroupeMurs, GroupeCaisses, GroupeBombes, GroupeFlammes, GroupePowerUps
from joueur import GroupeJoueurs
from map import Sol, Shadow
from config import ARENA_HEIGHT, ARENA_WIDTH


def main_function():
    if len(sys.argv) != 3:
        print "Usage: %s ip port" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    time_delay = .0

    pygame.init()

    screen = pygame.display.set_mode((ARENA_WIDTH * 32, ARENA_HEIGHT * 32), pygame.RESIZABLE)
    enCours = True
    clock = pygame.time.Clock()

    font = pygame.font.Font("assets/pixelmix.ttf", 20)
    font_bold = pygame.font.Font("assets/pixelmix_bold.ttf", 25)

    joueurs = GroupeJoueurs()
    client = BomberlanClient(ip, port, joueurs)
    murs = GroupeMurs()
    caisses = GroupeCaisses()
    bombes = GroupeBombes()
    flammes = GroupeFlammes()
    power_ups = GroupePowerUps()
    background = pygame.sprite.Group()

    for i in range(0, ARENA_WIDTH):
        for j in range(0, ARENA_HEIGHT):
            sol_center = (i * 32, j * 32)
            background.add(Sol(sol_center))

    music_played = "assets/track/fond.ogg"
    pygame.mixer.music.load(music_played)
    pygame.mixer.music.play(-1, 0.0)

    # Le jeu
    while enCours:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                enCours = False
                break

        joueurs.Pump()
        murs.Pump()
        caisses.Pump()
        bombes.Pump()
        flammes.Pump()
        power_ups.Pump()
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
        power_ups.draw(screen)
        bombes.draw(screen)
        joueurs.draw(screen)
        flammes.draw(screen)

        if not client.game_over and not client.game_won:
            if client.running:
                touches = pygame.key.get_pressed()
                client.Send({"action": "keys", "keys": touches})

            else:
                if client.game_start:
                    display_message(screen, font, client.game_start_message, (220, 220, 220))
                    client.running = True
                    time_delay = 1.0

                else:
                    display_message(screen, font, "En attente du serveur..", (220, 220, 220))
                    time_delay = .1

        elif client.game_over:
            if music_played == "assets/track/fond.ogg" :
                pygame.mixer.music.stop()
                music_played = "assets/track/perdu.ogg"
                pygame.mixer.music.load(music_played)
                pygame.mixer.music.play(1, 0.0)


            display_message(screen, font_bold, client.game_over_message, (255, 100, 100))
            time_delay = .05

        elif client.game_won:
            pygame.mixer.music.stop()
            display_message(screen, font_bold, client.game_won_message, (255, 100, 100))
            time_delay = .05

        pygame.display.flip()

        time.sleep(time_delay)
        time_delay = .001
    pygame.mixer.music.stop()


def display_message(screen, font, message, color):
    disp_message = font.render(message, True, color)

    disp_message_rect = disp_message.get_rect()
    disp_message_rect.topleft = ((screen.get_rect().width - disp_message_rect.width) / 2,
                                 (screen.get_rect().height - disp_message_rect.height) / 2)

    screen.blit(disp_message, disp_message_rect)

def checkMusic(music):


