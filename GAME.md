# Présentation du jeu et Règles (`GAME.md`)

## Principe du jeu
**Bomberman** est un jeu d'action et de stratégie se déroulant dans une arène quadrillée (`15 × 9` cases, mais seulement `13 × 7` accessibles). Le but est d'éliminer son adversaire (un autre joueur ou une IA) en posant des bombes qui explosent en croix après un court délai, tout en détruisant les murs destructibles pour ouvrir de nouveaux passages. Si

## Modes de jeu
* **Mode 1v1** : Deux joueurs s'affrontent en local sur le même clavier.
* **Mode PvE** : Le joueur doit passer quelques niveaux. Il y a plusieurs types d'ennemis rencontrés, ceux cherchant juste à toucher le joueur, et le **Boss**, un adversaire d'abord protégé par des piliers, à détruire pendant qu'il nous attaque, puis qui essaie de nous courir dessus, tuant le joueur sur le coup. Nous avons voulu faire en sorte que le joueur ait du challenge en jouant, donc au fur et à mesure du combat, le boss attaque de plus en plus vite.

## Règles et éléments de la carte
* **Sol (`Tile.passage`)** : Case libre sur laquelle les personnages peuvent se déplacer.
* **Murs indestructibles (`Tile.mur`)** : Obstacles fixes qui bloquent les déplacements et stoppent la propagation des flammes.
* **Murs cassables (`Tile.mur_cassable`)** : Obstacles pouvant être détruits par l'explosion d'une bombe, libérant ainsi le passage. Cela bloque aussi la propagation des flammes (un seul mur cassé dans une direction donnée).
* **Bombes, Flammes et Laser (`Tile.bomb` / `Tile.fire` / `Tile.fire_laser`)** : Une bombe posée explose après un minuteur. Tout personnage touché par les flammes perd **1 point de vie** (sur 3 points de vie initiaux pour les joueurs). La partie se termine lorsqu'un camp n'a plus de points de vie.

## Commandes

| Action | Joueur 1 | Joueur 2 (Mode 1v1) |
| :--- | :--- | :--- |
| **Haut / Bas / Gauche / Droite** | `Z` / `S` / `Q` / `D` | Flèches directionnelles |
| **Poser une bombe** | `Espace` | `Shift Droit` |
| **Retour au menu** | `M` | `M` |
| **Lancer la version debug(affichage de Dijkstra)** | `T` | `T` |
| **En mode PVE: passer au boss** | `B` | `B` |
| **En mode PVE: passer à la 2ème phase** | `O` | `O` |
| **En mode PVE: passer la dernière phase** | `P` | `P` |

