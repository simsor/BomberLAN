#!/usr/bin/env python2
# coding: utf-8

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import pygame
import sys

class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        self._server.del_client(self)
        
    def Network_keys(self, data):
        print "Received keys"


class MyServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        pygame.init()

        self.screen = pygame.display.set_mode((100, 100))
        self.clients = []
        self.clock = pygame.time.Clock()

        print "Serveur en écoute sur le port %d" % (port)

        self.main_loop()

    def Connected(self, channel, addr):
        print "Connexion de %s:%d" % (addr[0], addr[1])
        self.clients.append(channel)

    def del_client(self, channel):
        print "Client déconnecté"
        self.clients.remove(channel)

    def main_loop(self):
        while True:
            self.clock.tick(60)
            self.Pump()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s ip port" % (sys.argv[0])
        sys.exit(3)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    
    my_server = MyServer(localaddr = (ip, port))
