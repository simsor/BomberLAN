# coding: utf-8

import pygame
import time
import sys

from reseau import BomberlanClient, GroupeMurs, GroupeCaisses, GroupeBombes, GroupeFlammes, GroupePowerUps
from joueur import GroupeJoueurs
from map import Sol, Shadow
from functions import load_png
from config import ARENA_HEIGHT, ARENA_WIDTH, PLAYER_LIFE_MAX
from config import ASSET_BOMBE, ASSET_LIFE, ASSET_LIFE_GONE

SCREEN_COLOR = (0, 0, 0)
PANEL_WIDTH = 100


def main_function():
    if len(sys.argv) != 3:
        print "Usage: %s ip port" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    time_delay = .0

    pygame.init()

    screen = pygame.display.set_mode((ARENA_WIDTH * 32 + PANEL_WIDTH, ARENA_HEIGHT * 32), pygame.RESIZABLE)
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

        screen.fill(SCREEN_COLOR)
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
                else:
                    display_message(screen, font, "En attente du serveur..", (220, 220, 220))
                time_delay = .1

        elif client.game_over:
            display_message(screen, font_bold, client.game_over_message, (255, 100, 100))
            time_delay = .05

        elif client.game_won:
            display_message(screen, font_bold, client.game_won_message, (255, 100, 100))
            time_delay = .05

        show_stat_panel(screen, joueurs, bombes)

        pygame.display.flip()

        time.sleep(time_delay)
        time_delay = .001


def display_message(screen, font, message, color):
    disp_message = font.render(message, True, color)

    disp_message_rect = disp_message.get_rect()
    disp_message_rect.topleft = ((screen.get_rect().width - disp_message_rect.width) / 2,
                                 (screen.get_rect().height - disp_message_rect.height) / 2)

    screen.blit(disp_message, disp_message_rect)


def show_stat_panel(screen, joueurs, bombes):
    # Card width, card height
    card_width = PANEL_WIDTH - 10
    card_height = (ARENA_HEIGHT * 32) / (len(joueurs) + 1)

    # Scale ratio
    scale = 1.4

    # Récupération des bombes
    bombe_joueur = {}
    for j in joueurs:
        bombe_joueur[j.numero] = 0
    for bombe in bombes:
        bombe_joueur[bombe.joueur_id] += 1

    # Bombe definitions
    bombe_img, bombe_rect = load_png(ASSET_BOMBE)
    bombe_img_height = bombe_rect.height + 10

    # Life definitions
    life_img, life_rect = load_png(ASSET_LIFE)
    life_gone_img = load_png(ASSET_LIFE_GONE)[0]
    life_img_height = life_rect.height + 10

    # (width, height) center of the first card
    w_center = (ARENA_WIDTH * 32) + (card_width / 2)
    h_center = card_height / 2

    # Blit joueurs stats
    for joueur in joueurs:
        # Joueur's life blitting
        img_width = (card_width / (PLAYER_LIFE_MAX + 1))
        life_rect.center = ((ARENA_WIDTH * 32 + img_width), h_center)

        for i in range(joueur.life):
            screen.blit(life_img, life_rect)
            life_rect.centerx += img_width

        for i in range(PLAYER_LIFE_MAX - joueur.life):
            screen.blit(life_gone_img, life_rect)
            life_rect.centerx += img_width

        h_center += life_img_height

        # Joueur blitting
        image = pygame.transform.scale(joueur.image, (int(joueur.rect.width * scale), int(joueur.rect.height * scale)))
        rect = image.get_rect()
        rect.center = (w_center, h_center)
        screen.blit(image, rect)

        h_center += bombe_img_height

        # Joueur's bombes blitting
        img_width = (card_width / (bombe_joueur[joueur.numero] + 1))
        bombe_rect.center = ((ARENA_WIDTH * 32 + img_width), h_center)

        for i in range(bombe_joueur[joueur.numero]):
            screen.blit(bombe_img, bombe_rect)
            bombe_rect.centerx += img_width

        h_center += (card_height / 2)