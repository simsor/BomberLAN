# coding: utf-8

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

PLAYER_SPEED = 4
PLAYER_LIFE_MAX = 3

# La largeur et la hauteur devraient être des nombres impairs
ARENA_WIDTH = 17
ARENA_HEIGHT = 17

# Config des caisses
# Timer avant l'apparition d'une caisse (une vraie ..!)

CAISSE_DELAY = 1000
CAISSE_NOMBRE_MINI = 12

# Config de la bombe
# Timer avant explosion en frame

BOMB_DELAY = 120
BOMB_EXPLOSE_DELAY = 40
BOMB_RANGE = 2

# Images / assets :
# définition générale ici pour ne pas avoir à changer côté serveur et client à chaque fois

ASSET = "assets/"

ASSET_MUR = ASSET + "mur.png"
ASSET_CAISSE = ASSET + "caisse_2.png"
ASSET_BOMBE = ASSET + "bombe3.png"
ASSET_FLAME = ASSET + "flame.png"
ASSET_ANIMATE_FLAMES = {
    0: ASSET + "flame_1.png",
    1: ASSET + "flame_2.png",
    2: ASSET + "flame_3.png",
    3: ASSET + "flame_4.png"
}
ASSET_POWER_UP = {
    'flamme': ASSET + "power_up_flamme.png",
    'speed': ASSET + "power_up_speed.png",
    'bombe': ASSET + "power_up_bombe.png"
}
ASSET_JOUEUR = {
    'BAS': ASSET + "joueur_bas.png",
    'HAUT': ASSET + "joueur_haut.png",
    'DROITE': ASSET + "joueur_droite.png",
    'SHADOW': ASSET + "shadow.png"
}
ASSET_ENNEMI = {
    'BAS': ASSET + "ennemi_bas.png",
    'HAUT': ASSET + "ennemi_haut.png",
    'DROITE': ASSET + "ennemi_droite.png",
    'SHADOW': ASSET + "shadow.png"
}
ASSET_SOL = ASSET + "bg_1.png"
ASSET_LIFE = ASSET + "life.png"
ASSET_LIFE_GONE = ASSET + "life_gone.png"