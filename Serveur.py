#!/usr/bin/env python2
# coding: utf-8

import pygame
import random
import random
import sys

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from config import ARENA_HEIGHT, ARENA_WIDTH, CAISSE_DELAY, CAISSE_NOMBRE_MINI
from serveur.map import Mur, Caisse
from serveur.joueur import Joueur
from pgu import gui


class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        self._server.del_client(self)

    def update(self):
        self.joueur.update(self._server)
        for client in self._server.clients:
            self.Send({"action": "joueur_position",
                       "numero": client.joueur.numero,
                       "centre": client.joueur.rect.center,
                       "direction": client.joueur.direction,
                       "bouclier": client.joueur.bouclier,
                       'life': client.joueur.life})

    def Network_keys(self, data):
        touches = data["keys"]
        if touches[pygame.K_UP]:
            self.joueur.up()
        if touches[pygame.K_DOWN]:
            self.joueur.down()
        if touches[pygame.K_LEFT]:
            self.joueur.left()
        if touches[pygame.K_RIGHT]:
            self.joueur.right()
        if touches[pygame.K_SPACE]:
            self.joueur.poseBombe(self._server.bombes, self._server.clients)


class MyServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, localaddr=kwargs["localaddr"])
        pygame.init()

        self.nb_joueurs = kwargs["nb_joueurs"]

        self.screen = pygame.display.set_mode((48, 48))
        pygame.display.set_caption("BomberSERV @ " + kwargs["localaddr"][0])
        self.clients = []
        self.clock = pygame.time.Clock()

        self.murs = pygame.sprite.Group()
        self.caisses = pygame.sprite.Group()
        self.bombes = pygame.sprite.Group()
        self.flammes = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()

        self.icon_wait = pygame.image.load("assets/wait.png")
        self.icon_play = pygame.image.load("assets/bombe3.png")
        self.etat = self.icon_wait

        print "Serveur en écoute sur le port %d" % kwargs["localaddr"][1]
        print "En attente des %d joueurs .." % self.nb_joueurs

        # On crée une bordure de murs
        for i in range(0, ARENA_WIDTH):
            self.murs.add(Mur(i * 32, 0))
            self.murs.add(Mur(i * 32, ARENA_HEIGHT * 32 - 32))

        for i in range(1, ARENA_HEIGHT):
            self.murs.add(Mur(0, i * 32))
            self.murs.add(Mur(ARENA_WIDTH * 32 - 32, i * 32))

        # On crée la grille
        for i in range(1, ARENA_WIDTH - 2):
            for j in range(1, ARENA_HEIGHT - 2):
                if i % 2 == 0 and j % 2 == 0:
                    self.murs.add(Mur(i * 32, j * 32))

        # On crée les caisses : on rempli le centre, en ne laissant que les spawns de libres
        for i in range(3, ARENA_WIDTH - 3, 1):
            if random.randint(0, 100) <= 62:
                self.caisses.add(Caisse(i * 32, 1 * 32))
            if random.randint(0, 100) <= 62:
                self.caisses.add(Caisse(i * 32, (ARENA_HEIGHT - 2) * 32))

        for i in range(3, ARENA_HEIGHT - 3, 1):
            if random.randint(0, 100) <= 62:
                self.caisses.add(Caisse(1 * 32, i * 32))
            if random.randint(0, 100) <= 62:
                self.caisses.add(Caisse((ARENA_WIDTH - 2) * 32, i * 32))

        for i in range(2, ARENA_HEIGHT - 2, 1):
            if i % 2 == 0:
                for j in range(3, ARENA_WIDTH - 3, 2):
                    if random.randint(0, 100) <= 62:
                        self.caisses.add(Caisse(j * 32, i * 32))
            else:
                for j in range(2, ARENA_WIDTH - 2, 1):
                    if random.randint(0, 100) <= 62:
                        self.caisses.add(Caisse(j * 32, i * 32))

        # On crée les listes de centres de murs et de caisses
        self.centres_murs = [mur.rect.center for mur in self.murs]

        self.main_loop()

    def Connected(self, channel, addr):
        nb_player = len(self.clients)
        if nb_player >= self.nb_joueurs:
            channel.Send({'action': 'error', 'error': 'impossible de se connecter : le serveur est plein'})
            print "Impossible de connecter \"%s:%d\", le serveur est plein" % (addr[0], addr[1])
            print "Déconnection de \"%s:%d\"" % (addr[0], addr[1])
            return

        print "Bonjour \"%s:%d\" !" % (addr[0], addr[1])

        numeros = [c.joueur.numero for c in self.clients]
        for i in range(4):
            if not numeros.__contains__(i):
                nb_player = i
                break

        xSpawn = (1 + (ARENA_WIDTH - 3) * (nb_player % 2)) * 32
        ySpawn = (1 + (ARENA_HEIGHT - 3) * int(nb_player * 0.6)) * 32
        channel.joueur = Joueur(nb_player, (xSpawn, ySpawn))
        channel.Send({"action": "numero", "numero": channel.joueur.numero, 'life': channel.joueur.life})
        channel.Send(
            {"action": "spawn", "numero_joueur": channel.joueur.numero, "spawn_center": channel.joueur.spawn.center})

        # On envoie les murs
        channel.Send({"action": "murs", "murs_center": self.centres_murs})

        # On envoie les caisses, bombes, flammes et power-ups
        for caisse in self.caisses:
            channel.Send({'action': 'caisse', 'caisse_center': caisse.rect.center, 'caisse_id': caisse.id})
        for bombe in self.bombes:
            channel.Send({'action': 'bombe', 'bombe_center': bombe.rect.center, 'bombe_id': bombe.id,
                          'joueur_id': bombe.joueur.numero})
        for flamme in self.flammes:
            channel.Send({'action': 'flamme', 'flamme_center': flamme.rect.center, 'flamme_id': flamme.id})
        for powerUp in self.power_ups:
            channel.Send({'action': 'powerUp', 'powerUp_type': powerUp.type, 'powerUp_center': powerUp.rect.center,
                          'powerUp_id': powerUp.id})

        # On envoie les autres joueurs connectés avec leur spawn
        for c in self.clients:
            c.Send({"action": "joueur", "numero": channel.joueur.numero, 'life': channel.joueur.life})
            channel.Send({"action": "joueur", "numero": c.joueur.numero, 'life': c.joueur.life})
            c.Send({"action": "spawn", "numero_joueur": channel.joueur.numero,
                    "spawn_center": channel.joueur.spawn.center})
            channel.Send({"action": "spawn", "numero_joueur": c.joueur.numero, "spawn_center": c.joueur.spawn.center})

        self.clients.append(channel)

        if len(self.clients) == self.nb_joueurs:
            self.etat = self.icon_play
            for c in self.clients:
                c.Send({"action": "game_start", "message": "Gooooooooooo !!"})

    def del_client(self, channel):
        if not self.clients.__contains__(channel):
            return

        print "Client %d déconnecté" % (channel.joueur.numero)
        self.clients.remove(channel)
        for c in self.clients:
            c.Send({"action": "joueur_disconnected", "numero": channel.joueur.numero})

        if len(self.clients) == 0:
            print "LE SERVEUR SE CASSE - plus personne ne veut jouer :'("
            sys.exit(0)

    def check_win(self):
        if len(self.clients) == 1:
            print "Victoire du joueur %d ! Bravo (il est très fort !)" % (self.clients[0].joueur.numero)
            self.clients[0].Send({'action': 'game_won', 'message': 'V I C T O I R E  !!'})
            print "FIN DU JEU - à la prochaine :)"
            self.running = False


    def channelByNumero(self, numero):
        return [c for c in self.clients if c.joueur.numero == numero][0]


    def randomize_caisse(self):
        toplefts = [m.rect.topleft for m in self.murs]
        toplefts += [c.rect.topleft for c in self.caisses]
        toplefts += [b.rect.topleft for b in self.bombes]
        toplefts += [f.rect.topleft for f in self.flammes]
        toplefts += [p.rect.topleft for p in self.power_ups]
        toplefts += [c.joueur.rect.topleft for c in self.clients]
        toplefts += [c.joueur.spawn.topleft for c in self.clients]

        possible_toplefts = []

        for i in range(ARENA_WIDTH):
            for j in range(ARENA_HEIGHT):
                topleft = (i * 32, j * 32)
                if not toplefts.__contains__(topleft):
                    possible_toplefts.append(topleft)

        xAbs, yAbs = possible_toplefts[random.randint(0, len(possible_toplefts) - 1)]
        caisse = Caisse(xAbs, yAbs)
        for c in self.clients:
            c.Send({'action': 'caisse', 'caisse_center': caisse.rect.center, 'caisse_id': caisse.id})

        return caisse


    def main_loop(self):
        """
        Boucle principale du serveur : boucle de jeu
        """
        self.running = True
        self.nb_caisses_explosees = 0
        caisse_timer = CAISSE_DELAY

        while self.running:
            self.clock.tick(60)

            # On update les bombes
            self.bombes.update(self)

            # On update les flammes
            self.flammes.update(self)

            # On update les caisses
            self.caisses.update(self)

            # On envoie toutes les données aux clients
            for c in self.clients:
                c.update()

            if self.nb_caisses_explosees > CAISSE_NOMBRE_MINI:
                caisse_timer -= 1
                if caisse_timer == 0:
                    self.caisses.add(self.randomize_caisse())
                    caisse_timer = CAISSE_DELAY - ((self.nb_caisses_explosees - CAISSE_NOMBRE_MINI) * 10)
                    if caisse_timer > CAISSE_DELAY / 2:
                        caisse_timer = CAISSE_DELAY / 2

            self.Pump()

            self.screen.fill((255, 255, 255))
            self.screen.blit(self.etat, (0, 0))

            pygame.display.flip()


if __name__ == "__main__":
    # On évite PGU pour Michel
    if len(sys.argv) >= 4 and sys.argv[1] == "--michel":
        ip = sys.argv[2]
        port = int(sys.argv[3])
        if len(sys.argv) == 5:
            nb = int(sys.argv[4])
        else:
            nb = 2
        MyServer(localaddr=(ip, port), nb_joueurs=nb)
    else:
        # Les autres ont le droit à une interface jolie
        app = gui.Desktop(title="coucou", theme=gui.Theme("data/themes/clean"))
        app.connect(gui.QUIT, app.quit, None)
        
        table = gui.Table()
        
        # Titre
        table.tr()
        table.td(gui.Label("Config serveur"), colspan=4)
        
        # IP du serveur
        table.tr()
        table.td(gui.Label("IP : "))
        
        champ_ip = gui.Input(value="0.0.0.0", size=15)
        table.td(champ_ip, colspan=3)
        
        # Port d'écoute
        table.tr()
        table.td(gui.Label("Port : "))
        
        champ_port = gui.Input(value="8888", size=5)
        table.td(champ_port, colspan=3)
        
        # Nombre de joueurs
        table.tr()
        table.td(gui.Label("Nombre joueurs :"))
        
        slider_nb = gui.HSlider(value=2, min=2, max=4, size=5, width=150)
        champ_nb = gui.Label("2")
        
        def maj_nb(valeurs):
            (champ, slider) = valeurs
            champ.value = str(slider.value)
            champ.repaint()
            
        slider_nb.connect(gui.CHANGE, maj_nb, (champ_nb, slider_nb))
        
        table.td(slider_nb, colspan=3)
        table.tr()
        table.td(champ_nb, colspan=4)
        
        # Bouton GO
        table.tr()
        bouton_go = gui.Button(value="GO !")
        
        def lancer_jeu(valeurs):
            (ip, port, nb) = valeurs
            MyServer(localaddr=(ip.value, int(port.value)), nb_joueurs=int(nb.value))
            
        bouton_go.connect(gui.CLICK, lancer_jeu, (champ_ip, champ_port, champ_nb))
        table.td(bouton_go)
        
        app.run(table)
