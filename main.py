# Example file showing a circle moving on screen
import pygame
import os

# Import des Classes
from player import Player
from tile import Tile
from bomb import Bomb
from Ai import *

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1030, 630))
clock = pygame.time.Clock()
running = True
dt = 0

# map
map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],[1,0,0,2,2,2,2,2,2,2,2,2,0,0,1], [1,0,1,2,1,2,1,2,1,2,1,2,1,0,1],[1,2,2,2,2,2,2,2,2,2,2,2,2,2,1],[1,2,1,2,1,2,1,2,1,2,1,2,1,2,1],[1,2,2,2,2,2,2,2,2,2,2,2,2,2,1] ,[1,2,1,2,1,2,1,2,1,2,1,2,1,2,1],[1,0,0,2,2,2,2,2,2,2,2,2,0,0,1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

# creation grille de jeu

grille_du_jeu = []

for y, ligne in enumerate(map):
    ligne_de_tiles = []
    for x, valeur in enumerate(ligne):
        # 1 = mur, 2 = mur_cassable, sinon passage
        if valeur == 1:
            t_type = "mur"
        elif valeur == 2:
            t_type = "mur_cassable"
        else:
            t_type = "passage"
            
        nouvelle_tile = Tile(x, y, t_type)
        ligne_de_tiles.append(nouvelle_tile)
        
    grille_du_jeu.append(ligne_de_tiles)


# chargement des images
surf_original = pygame.image.load(os.path.join('Sprites', 'Sprite_char.png')).convert_alpha()
bg_original = pygame.image.load(os.path.join('Sprites', 'BG.png')).convert()


# Redimensionnement des images pour avoir un style pixélisé 
bg = pygame.transform.scale(bg_original, (1030, 630))
surf = pygame.transform.scale(surf_original, (44, 50)) 

# Position initiale du joueur au centre
player_pos = pygame.Vector2(70,70)
player_speed = 300  # Vitesse en px/s

liste_bombes = []


#Joueur 1
player1 = Player('test', 3, player_pos.x, player_pos.y)
player2 = Player('Robot', 3, player_pos.x, player_pos.y)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bombe_suiv = Bomb(player1.pos.x, player1.pos.y)
                        liste_bombes.append(bombe_suiv)
                    if event.key == pygame.K_RSHIFT:
                            bombe_suiv = Bomb(player2.pos.x, player2.pos.y)
                            liste_bombes.append(bombe_suiv)

    screen.fill("grey")

    # Affichage du fond d'écran en premier
    screen.blit(bg, (0, 0))

    for ligne in grille_du_jeu:
        for tile in ligne:
            tile.draw(screen)
    


    keys = pygame.key.get_pressed()

    

    if keys[pygame.K_e]:
        running = False  # Quitter la boucle


    for bombe in liste_bombes[:]: 
        bombe.update(grille_du_jeu)
        grille_du_jeu = bombe.draw(screen, grille_du_jeu)
        if bombe.etat == "détruite":
            liste_bombes.remove(bombe)


    # --- Affichage du joueur ---

    player1.show(surf,screen)
    player2.show(surf,screen)

    # Mouvement Joueur
    player1.move(dt,keys,grille_du_jeu,1)
    player2.move(dt,keys,grille_du_jeu,2)
    #Mouvement AI (test)

    # Mettre à jour l'affichage de l'écran
    pygame.display.flip()

    # Limite à 60 FPS et calcul du dt (en secondes)
    dt = clock.tick(60) / 1000

pygame.quit()
