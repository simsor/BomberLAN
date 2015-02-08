# BomberLAN
Un Bomberman fait avec Pygame et PodSixNet pour le réseau.

## Définitions
- *Mur*: indestructible, présent autour de l'arène et en grille au centre
- *Caisse*: destructible (par bombe), peut lâcher un powerup

## Liste des powerups (à améliorer)
- *Portée+*: augmente la portée des bombes
- *Vitesse+*: augmente la vitesse de déplacement du joueur
- *Bouclier*: permet de survivre à une bombe
- *Télécommande*: permet de faire exploser une bombe à la demande

## Modèle choisi
Le modèle utilisé est celui d'un client "bête". Le client envoie les touches au serveur, qui répond avec l'état de tous les objets.
A chaque frame, le serveur envoie la liste des murs, des caisses, des joueurs, des bombes, des explosions.
