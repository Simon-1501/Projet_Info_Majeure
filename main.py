# Example file showing a circle moving on screen
import pygame
import os

# Import des Classes
from player import Player
from tile import Tile
from Ai import *



#var
tile_x = 70
tile_y = 70
screen_size_x = 1050
screen_size_y = 630


# pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_size_x, screen_size_y))
clock = pygame.time.Clock()
running = True
dt = 0

# map
map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],[1,0,0,2,2,2,2,2,2,2,2,2,0,0,1], [1,0,1,2,1,2,1,2,1,2,1,2,1,0,1],[1,2,2,2,2,2,2,2,2,2,2,2,2,2,1],[1,2,1,2,1,2,1,2,1,2,1,2,1,2,1],[1,2,2,2,2,2,2,2,2,2,2,2,2,2,1] ,[1,0,1,2,1,2,1,2,1,2,1,2,1,0,1],[1,0,0,2,2,2,2,2,2,2,2,2,0,0,1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

# creation grille de jeu

grille_du_jeu = []

for y, ligne in enumerate(map):
    ligne_de_tiles = []
    for x, valeur in enumerate(ligne):
        # On passe la position en pixels ET les index x, y de la matrice
        nouvelle_tile = Tile(x*tile_x, y*tile_y, x, y) 
        
        # 1 = mur, 2 = mur_cassable, sinon passage
        if valeur == 1:
            nouvelle_tile.send("build")
        elif valeur == 2:
            nouvelle_tile.send("build_cassable")

        ligne_de_tiles.append(nouvelle_tile)
        
    grille_du_jeu.append(ligne_de_tiles)


# chargement des images
player1 = pygame.image.load(os.path.join('Sprites', 'PLAYER1.png')).convert_alpha()
player2 = pygame.image.load(os.path.join('Sprites', 'PLAYER2.png')).convert_alpha()

bg_original = pygame.image.load(os.path.join('Sprites', 'BG.png')).convert()


# Redimensionnement des images pour avoir un style pixélisé 
bg = pygame.transform.scale(bg_original, (screen_size_x, screen_size_y))
player1 = pygame.transform.scale(player1, (70, 70)) 
player2 = pygame.transform.scale(player2, (70, 70)) 



# Position initiale du joueur 
player_pos = pygame.Vector2(70,70)


#Joueursd
players = [Player(player1, 'Joueur 1', 3, player_pos.x, player_pos.y, pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE), Player(player2, 'Joueur 2', 3,910, 70, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT)]


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            for player in players:
                if event.key == player.keybomb and player.est_vivant():
                        grille_du_jeu[int(player.pos_grille[1])][int(player.pos_grille[0])].drop()
            
    screen.fill("grey")

    # Affichage du fond d'écran en premier
    screen.blit(bg, (0, 0))

    for ligne in grille_du_jeu:
        for tile in ligne:
            tile.draw(screen)
            tile.update(dt, grille_du_jeu)

    


    keys = pygame.key.get_pressed()

    

    if keys[pygame.K_e]:
        running = False  # Quitter la boucle


    # Joueure
    for player in players:
        if player.est_vivant():
            player.show(screen)
            player.update(grille_du_jeu, dt)
            player.move(dt,keys,grille_du_jeu)


    #Mouvement AI (test)

    # Mettre à jour l'affichage de l'écran
    pygame.display.flip()

    # Limite à 60 FPS et calcul du dt (en secondes)
    dt = clock.tick(60) / 1000

pygame.quit()
