# Example file showing a circle moving on screen
import pygame
import os


# Import des Classes
from player import Player
from tile import Tile
from AI import *
from button import Bouton


# Chargement modèles IA

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

codes_terrain = {Tile.passage: 0,
                 Tile.mur: 1,
                 Tile.mur_cassable: 2,
                 Tile.bomb: 3,
                 Tile.fire: 4
                 }

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
boutton_play = pygame.image.load(os.path.join('Sprites', 'PLAYER2.png')).convert_alpha()

bg_original_menu = pygame.image.load(os.path.join('Sprites', 'BG.png')).convert()
bg_original_menu_choix = pygame.image.load(os.path.join('Sprites', 'BG_mode_jeu.png')).convert()

# Redimensionnement des images pour avoir un style pixélisé 
bg_menu = pygame.transform.scale(bg_original_menu, (screen_size_x, screen_size_y))
bg_menu_choix = pygame.transform.scale(bg_original_menu_choix, (screen_size_x, screen_size_y))

player1 = pygame.transform.scale(player1, (70, 70)) 
player2 = pygame.transform.scale(player2, (70, 70)) 
AI1 = pygame.transform.scale(player2, (70, 70)) 

# Position initiale du joueur 
player1_pos = (1,1)
player2_pos = (13,7)
AI_pos = (13,7)

#Joueurs
players = [Player(1, 'Joueur 1', 3, player1_pos[0], player1_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE), 
           Player(2, 'Joueur 2', 3, player2_pos[0], player2_pos[1], pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT)]

player_speed = 300  # Vitesse en px/s

state = 'PVE'
clic = False
tap = False
AI1 = AI(player2,'bot', 3, AI_pos[0], AI_pos[1])
#Joueurs

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            tap = True
            for player in players:
                if event.key == player.keybomb and player.est_vivant():
                        grille_du_jeu[int(player.pos_grille[1])][int(player.pos_grille[0])].drop()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            tap = True
            clic = True
            clic_posx, clic_posy = pygame.mouse.get_pos()
    screen.fill("grey")

    if state == 'menu':
        screen.blit(bg_menu,(0,0))
        if tap:
            state = 'menu choix mode de jeu'
        pygame.display.flip()

    elif state == 'menu choix mode de jeu':
        screen.blit(bg_menu_choix,(0,0))
        if clic:
            if clic_posx >=980 and clic_posy <= 70:
                running = False
            elif 630>=clic_posx>=420 and 140<=clic_posy<= 280:
                state = '1v1'
            
            pygame.display.flip()



    elif state == '1v1':

        # Affichage du fond d'écran en premier

        for ligne in grille_du_jeu:
            for tile in ligne:
                tile.draw(screen)
                tile.update(dt, grille_du_jeu)

    # Mettre à jour l'affichage de l'écran
       
        keys = pygame.key.get_pressed()

        if keys[pygame.K_e]:
            running = False  # Quitter la boucle

        # Joueur
        for player in players:
            if player.est_vivant():
                player.update(grille_du_jeu, dt)
                player.move(dt,keys,grille_du_jeu)
                player.show(screen)

        
        # Mettre à jour l'affichage de l'écran
        pygame.display.flip()

        # Limite à 60 FPS et calcul du dt (en secondes)
        dt = clock.tick(60) / 1000
    if state == 'PVE':
       
                       
        for ligne in grille_du_jeu:
            for tile in ligne:
                tile.draw(screen)
                tile.update(dt, grille_du_jeu)
        
            # Mettre à jour l'affichage de l'écran
        
        keys = pygame.key.get_pressed()
               
        if keys[pygame.K_e]:
            running = False  # Quitter la boucle

        if AI1.est_vivant():
            AI1.show(screen)
            AI1.update(grille_du_jeu, dt)

        if players[0].est_vivant():
            players[0].show(screen)
            players[0].update(grille_du_jeu,dt)
            players[0].move(dt, keys, grille_du_jeu)

        #Mouvement AI (test)
        
        AI1.moveAI(dt,(players[0].pos_grille[0],players[0].pos_grille[1]),(AI1.pos_grille[0],AI1.pos_grille[1]),grille_du_jeu) #c'est au point zebi 

        #Mettre à jour l'affichage de l'écran
        pygame.display.flip()
        
        # Limite à 60 FPS et calcul du dt (en secondes)
        dt = clock.tick(60) / 1000


pygame.quit()
