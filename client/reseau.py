# coding: utf-8

import sys
import pygame

from PodSixNet.Connection import connection, ConnectionListener

from joueur import Joueur
from map import Caisse, Mur, Bombe, Flamme, PowerUpFlamme, PowerUpSpeed, PowerUpBombe, PowerUpShield, Spawn
from config import ASSET_SOUND


class BomberlanClient(ConnectionListener):
    # Variable de classe représentant le numéro du joueur

    def __init__(self, ip, port, groupe_joueurs):
        self.running = False  # On ne lance le jeu que quand au moins 2 joueurs sont connectés
        self.game_start = False
        self.game_over = False
        self.game_won = False
        self.Connect((ip, port))
        self.groupe_joueurs = groupe_joueurs

    def Network_connected(self, data):
        print "Connecté au serveur !"

    def Network_error(self, data):
        print 'error:', data['error']
        connection.Close()
        sys.exit(2)

    def Network_disconnected(self, data):
        print 'Server disconnected'

    def Network_numero(self, data):
        print "Je suis le client numéro %d" % data["numero"]
        Joueur.numeroJoueur = data["numero"]
        self.groupe_joueurs.add(Joueur(data["numero"], data['life']))

    def Network_game_start(self, data):
        self.game_start = True
        self.game_start_message = data['message']

    def Network_game_over(self, data):
        self.running = False
        self.game_over = True
        self.game_over_message = data['message']

    def Network_game_won(self, data):
        self.running = False
        self.game_won = True
        self.game_won_message = data['message']

    def Loop(self):
        connection.Pump()
        self.Pump()


class GroupeMurs(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de murs qui écoute sur le réseau """

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_murs(self, data):
        self.empty()
        for mur_center in data["murs_center"]:
            self.add(Mur(mur_center))


class GroupeCaisses(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de caisses qui écoute sur le réseau """

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_caisse(self, data):
        self.add(Caisse(data['caisse_id'], data['caisse_center']))

    def Network_caisse_remove(self, data):
        self.caisseById(data['caisse_id']).kill()

    def caisseById(self, id):
        return [c for c in self if c.id == id][0]


class GroupeFlammes(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de flammes qui écoute sur le réseau """

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_flamme(self, data):
        self.add(Flamme(data['flamme_id'], data['flamme_center']))

    def Network_flamme_remove(self, data):
        self.flammeById(data['flamme_id']).kill()

    def flammeById(self, id):
        return [f for f in self if f.id == id][0]


class GroupeBombes(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de bombes qui écoute le réseau"""

    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.son_explosion = pygame.mixer.Sound(ASSET_SOUND['bombe'])

    def Network_bombe(self, data):
        self.add(Bombe(data['bombe_id'], data['bombe_center'], data['joueur_id']))

    def Network_bombe_remove(self, data):
        self.bombeById(data['bombe_id']).kill()
        self.son_explosion.play()

    def bombeById(self, id):
        return [b for b in self if b.id == id][0]


class GroupePowerUps(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de power ups qui écoute le réseau"""

    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.son_pickup = pygame.mixer.Sound(ASSET_SOUND['powerup'])

    def Network_powerUp(self, data):
        if data["powerUp_type"] == "flamme":
            self.add(PowerUpFlamme(data["powerUp_id"], data["powerUp_center"]))
        elif data["powerUp_type"] == "speed":
            self.add(PowerUpSpeed(data["powerUp_id"], data["powerUp_center"]))
        elif data["powerUp_type"] == "bombe":
            self.add(PowerUpBombe(data["powerUp_id"], data["powerUp_center"]))
        elif data["powerUp_type"] == "shield":
            self.add(PowerUpShield(data["powerUp_id"], data["powerUp_center"])) 

    def Network_powerUp_remove(self, data):
        self.powerUpById(data['powerUp_id']).kill()
        self.son_pickup.play()

    def powerUpById(self, id):
        return [b for b in self if b.id == id][0]


class GroupeSpawns(pygame.sprite.Group, ConnectionListener):
    """ Représente un groupe de spawns qui écoute le réseau"""

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def Network_spawn(self, data):
        self.add(Spawn(data['numero_joueur'], data['spawn_center']))
