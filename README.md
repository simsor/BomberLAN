# BomberLAN
Un Bomberman fait avec Pygame et PodSixNet pour le réseau.

## Définitions
- *Mur*: indestructible, présent autour de l'arène et en grille au centre
- *Caisse*: destructible (par bombe), peut lâcher un powerup
- *Powerup*: objet donnant divers effets au joueur qui le récupère.

## Liste des powerups (à améliorer)
- *Portée+*: augmente la portée des bombes
- *Vitesse+*: augmente la vitesse de déplacement du joueur
- *Bouclier*: permet de survivre à une bombe
- *Bombe+*: le joueur peut poser une bombe de plus (de base, il ne peut en poser qu'une)

## Modèle choisi
Le modèle utilisé est celui d'un client "bête". Le client envoie les touches au serveur, qui répond avec les changement d'état des objets.

A la connexion, le serveur envoie la liste des caisses et des murs. Quand il y a un changement, il notifie les clients de celui-ci. Les clients mettent à jour leurs données pour refléter le changement. Ce système permet d'éviter d'avoir à envoyer toute la map à chaque changement et donc d'optimiser la charge réseau

## Jouer

Cloner le dépôt ou télécharger le zip, puis double-cliquer sur Serveur.py pour lancer le serveur. Choisir l'IP et le port d'écoute, le nombre de joueurs avant de lancer le serveur.

Lancer ensuite Client.py, spécifier l'IP et le port du serveur et cliquer sur "Connexion". Une petite liste des touches est donnée au début du jeu pour préparer à la bataille.

## Tirer sur les problèmes

Sous Mac, il peut y avoir quelques problèmes avec la bibliothèque PGU utilisée pour faire l'interface graphique de début. Utiliser l'option --michel pour spécifier le serveur en ligne de commande.

```
./[Client.py|Serveur.py] --michel ip port [nb_joueurs]
```
