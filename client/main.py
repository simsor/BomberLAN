# coding: utf-8

import pygame
import time
import sys

from reseau import BomberlanClient, GroupeMurs, GroupeCaisses, GroupeBombes, GroupeFlammes, GroupePowerUps, GroupeSpawns
from joueur import GroupeJoueurs
from map import Sol, Shadow
from functions import load_png
from config import ARENA_HEIGHT, ARENA_WIDTH, PLAYER_LIFE_MAX, SIDE_LENGTH
from config import ASSET_BOMBE, ASSET_LIFE, ASSET_LIFE_GONE, ASSET_MUSIC, ASSET_JOUEUR, ASSET_SOL
from pgu import gui

SCREEN_COLOR = (0, 0, 0)
PANEL_WIDTH = 100


def main_function():
    app = gui.Desktop(theme=gui.Theme("data/themes/clean"))
    app.connect(gui.QUIT, app.quit, None)

    table = gui.Table()

    # Titre
    table.tr()
    table.td(gui.Label("Connexion au serveur"), colspan=4)

    # IP
    table.tr()
    table.td(gui.Label("IP :"))

    champ_ip = gui.Input(value="127.0.0.1", size=15)
    table.td(champ_ip, colspan=3)

    # Port d'écoute
    table.tr()
    table.td(gui.Label("Port : "))

    champ_port = gui.Input(value="8888", size=5)
    table.td(champ_port, colspan=3)

    # Bouton connexion
    table.tr()
    bouton_conn = gui.Button("Connexion")
    table.td(bouton_conn)

    def lancer_jeu(valeurs):
        (ip, port) = valeurs
        jeu(ip.value, int(port.value))
        sys.exit(0)

    bouton_conn.connect(gui.CLICK, lancer_jeu, (champ_ip, champ_port))

    app.run(table)


def jeu(ip, port):
    pygame.init()
    screen = pygame.display.set_mode((ARENA_WIDTH * SIDE_LENGTH + PANEL_WIDTH, ARENA_HEIGHT * SIDE_LENGTH),
                                     pygame.RESIZABLE)
    pygame.display.set_caption("BomberLAN @ " + ip)

    init_game(screen)
    time_delay = .0
    enCours = True
    clock = pygame.time.Clock()

    font = pygame.font.Font("assets/font/pixelmix.ttf", 20)
    font_bold = pygame.font.Font("assets/font/pixelmix_bold.ttf", 25)

    joueurs = GroupeJoueurs()
    client = BomberlanClient(ip, port, joueurs)
    murs = GroupeMurs()
    caisses = GroupeCaisses()
    spawns = GroupeSpawns()
    bombes = GroupeBombes()
    flammes = GroupeFlammes()
    power_ups = GroupePowerUps()
    background = pygame.sprite.Group()

    for i in range(0, ARENA_WIDTH):
        for j in range(0, ARENA_HEIGHT):
            sol_center = (i * SIDE_LENGTH, j * SIDE_LENGTH)
            background.add(Sol(sol_center))

    music_played = ASSET_MUSIC['fond']
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
        spawns.Pump()
        bombes.Pump()
        flammes.Pump()
        power_ups.Pump()
        client.Loop()

        joueurs.update(spawns)
        flammes.update(joueurs)

        screen.fill(SCREEN_COLOR)
        background.draw(screen)

        for j in joueurs:
            xAbs, yAbs = j.rect.midbottom
            shadow = Shadow((xAbs, yAbs - 8))
            screen.blit(shadow.image, shadow.rect)

        murs.draw(screen)
        caisses.draw(screen)
        spawns.draw(screen)
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
            if music_played != ASSET_MUSIC['perdu']:
                pygame.mixer.music.stop()
                music_played = ASSET_MUSIC['perdu']
                pygame.mixer.music.load(music_played)
                pygame.mixer.music.play(1, 0.0)

            display_message(screen, font_bold, client.game_over_message, (255, 100, 100))
            time_delay = .05

        elif client.game_won:
            if music_played != ASSET_MUSIC['gagne']:
                pygame.mixer.music.stop()
                music_played = ASSET_MUSIC['gagne']
                pygame.mixer.music.load(music_played)
                pygame.mixer.music.play(1, 0.0)

            display_message(screen, font_bold, client.game_won_message, (255, 100, 100))
            time_delay = .05

        show_stat_panel(screen, joueurs, bombes)

        pygame.display.flip()

        time.sleep(time_delay)
        time_delay = .001
    pygame.mixer.music.stop()


def display_message(screen, font, message, color, rect=0):
    if rect == 0:
        rect = screen.get_rect()

    disp_message = font.render(message, True, color)
    disp_message_rect = disp_message.get_rect()
    disp_message_rect.topleft = ((rect.width - disp_message_rect.width) / 2,
                                 (rect.height - disp_message_rect.height) / 2)

    screen.blit(disp_message, disp_message_rect)


def show_stat_panel(screen, joueurs, bombes):
    # Card width, card height
    card_width = PANEL_WIDTH - 10
    card_height = (ARENA_HEIGHT * SIDE_LENGTH) / (len(joueurs) + 1)

    # Scale ratio
    scale = 1.4

    # Récupération des bombes
    bombe_joueur = {}
    for j in joueurs:
        bombe_joueur[j.numero] = 0
    for bombe in bombes:
        if (bombe.joueur_id in bombe_joueur.keys()):
            bombe_joueur[bombe.joueur_id] += 1

    # Bombe definitions
    bombe_img, bombe_rect = load_png(ASSET_BOMBE)
    bombe_img_height = bombe_rect.height + 10

    # Life definitions
    life_img, life_rect = load_png(ASSET_LIFE)
    life_gone_img = load_png(ASSET_LIFE_GONE)[0]
    life_img_height = life_rect.height + 10

    # (width, height) center of the first card
    w_center = (ARENA_WIDTH * SIDE_LENGTH) + (card_width / 2)
    h_center = card_height / 2

    # Blit joueurs stats
    for joueur in joueurs:
        # Joueur's life blitting
        img_width = (card_width / (PLAYER_LIFE_MAX + 1))
        life_rect.center = ((ARENA_WIDTH * SIDE_LENGTH + img_width), h_center)

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
        bombe_rect.center = ((ARENA_WIDTH * SIDE_LENGTH + img_width), h_center)

        for i in range(bombe_joueur[joueur.numero]):
            screen.blit(bombe_img, bombe_rect)
            bombe_rect.centerx += img_width

        h_center += (card_height / 2)


def init_game(screen):
    """ Initialization game dialog """
    screen.fill((0, 0, 0))

    font_title = pygame.font.Font("assets/font/pacifico.ttf", 45)
    font_normal = pygame.font.Font("assets/font/aller_regular.ttf", 25)

    images_joueur = {
        'bas': load_png(ASSET_JOUEUR['BAS'])[0],
        'haut': load_png(ASSET_JOUEUR['HAUT'])[0],
        'droite': load_png(ASSET_JOUEUR['DROITE'])[0],
    }
    images_joueur['gauche'] = pygame.transform.flip(images_joueur['droite'], True, False)
    image_fond, image_fond_rect = None, None
    image_shadow, image_shadow_rect = None, None
    image_joueur, image_joueur_rect = None, (screen.get_rect().centerx - 16, screen.get_rect().centery - 16)

    title_rect = screen.get_rect()
    title_rect.height /= 2
    display_message(screen, font_title, "Initialisation", (152, 152, 100), title_rect)

    message_rect = screen.get_rect()
    message_rect.height *= 1.5
    display_message(screen, font_normal, "Appuyez sur espace", (172, 172, 100), message_rect)

    pygame.display.flip()

    key_to_press = 'espace'
    pressed = {
        'espace': False,
        'haut': False,
        'droite': False,
        'bas': False,
        'gauche': False
    }
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    if not pressed['espace']:
                        image_fond, image_fond_rect = load_png(ASSET_SOL)
                        image_fond_rect.center = screen.get_rect().center
                        image_shadow, image_shadow_rect = load_png(ASSET_JOUEUR['SHADOW'])
                        image_shadow_rect.center = screen.get_rect().center
                        pressed['espace'] = True
                        key_to_press = 'haut'

                    all_pressed = True
                    for value in pressed.values():
                        all_pressed = (all_pressed and value)

                    print all_pressed

                    if all_pressed:
                        screen.fill((0, 0, 0))
                        display_message(screen, font_title, "C'est parti  !  (on va gagner)", (152, 152, 100))
                        pygame.display.flip()
                        time.sleep(1.75)
                        return

                elif event.key == pygame.K_UP:
                    if not pressed['haut'] and pressed['espace']:
                        pressed['haut'] = True
                        key_to_press = 'gauche'
                    image_joueur = images_joueur['haut']

                elif event.key == pygame.K_LEFT:
                    if not pressed['gauche'] and pressed['haut']:
                        pressed['gauche'] = True
                        key_to_press = 'bas'
                    image_joueur = images_joueur['gauche']

                elif event.key == pygame.K_DOWN:
                    if not pressed['bas'] and pressed['gauche']:
                        pressed['bas'] = True
                        key_to_press = 'droite'
                    image_joueur = images_joueur['bas']

                elif event.key == pygame.K_RIGHT:
                    if not pressed['droite'] and pressed['bas']:
                        pressed['droite'] = True
                        key_to_press = 'espace pour jouer !'
                    image_joueur = images_joueur['droite']

        screen.fill((0, 0, 0))
        display_message(screen, font_title, "Initialisation", (152, 152, 100), title_rect)
        display_message(screen, font_normal, "Appuyez sur " + key_to_press, (172, 172, 100), message_rect)

        if pressed['espace']:
            screen.blit(image_fond, image_fond_rect)
            screen.blit(image_shadow, image_shadow_rect)

            if pressed['haut']:
                screen.blit(image_joueur, image_joueur_rect)

        pygame.display.flip()