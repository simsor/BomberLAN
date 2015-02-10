# coding: utf-8

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

PLAYER_SPEED = 4

# La largeur et la hauteur devraient être des nombres impairs
ARENA_WIDTH = 17
ARENA_HEIGHT = 17

# Config de la bombe
# Timer avant explosion en frame

BOMB_DELAY = 120
BOMB_RANGE = 2

# Images / assets :
# définition générale ici pour ne pas avoir à changer côté serveur et client à chaque fois

ASSET = "assets/"

ASSET_MUR = ASSET + "mur.png"
ASSET_CAISSE = ASSET + "caisse_2.png"
ASSET_BOMBE = ASSET + "bombe3.png"
ASSET_JOUEUR = {
    'BAS': ASSET + "joueur_bas.png",
    'HAUT': ASSET + "joueur_haut.png",
    'DROITE': ASSET + "joueur_droite.png",
    'SHADOW': ASSET + "shadow.png"
}
ASSET_SOL = ASSET + "bg_1.png"