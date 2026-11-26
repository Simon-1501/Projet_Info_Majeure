# Example file showing a circle moving on screen
import pygame
import os


# Import des Classes
from player import Player
from tile import Tile
from Ai import AI
from boss import Boss
from Recherche_Boss import creer_graph_boss
from labyrinthe import *


#var
tile_x = 70
tile_y = 70
screen_size_x = 1050
screen_size_y = 630
Ai_spawn_delay = 5
nb_active_AI = 1

state = 'boss'
clic = False
tap = False

# Position initiale du joueur 
player1_pos = (1,1)
player2_pos = (13,7)
AI_pos = (13,7)



# pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_size_x, screen_size_y))
clock = pygame.time.Clock()
running = True
dt = 0

# map
map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],[1,0,0,2,2,2,2,2,2,2,2,2,0,0,1], [1,0,1,2,1,2,1,2,1,2,1,2,1,0,1],[1,0,2,2,2,2,2,2,2,2,2,2,2,2,1],[1,0,1,2,1,2,1,2,1,2,1,2,1,2,1],[1,0,2,2,2,2,2,2,2,2,2,2,2,2,1] ,[1,0,1,2,1,2,1,2,1,2,1,2,1,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

map1 = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,2,0,0,2,0,2,0,0,2,0,0,1], 
        [1,0,0,0,2,0,0,0,0,0,2,0,0,0,1],
        [1,0,0,0,0,0,2,1,2,0,0,0,0,0,1],
        [1,0,1,2,1,0,1,1,1,0,1,2,1,0,1],
        [1,0,0,0,0,0,2,1,2,0,0,0,0,0,1],
        [1,0,0,0,2,0,0,0,0,0,2,0,0,0,1],
        [1,0,0,2,0,0,2,0,2,0,0,2,0,0,1], 
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]
# creation grille de jeu

codes_terrain = {Tile.passage: 0,
                 Tile.mur: 1,
                 Tile.mur_cassable: 2,
                 Tile.bomb: 3,
                 Tile.fire: 4
                 }

grille_du_jeu = []
grille_du_jeu1 = []

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

nb_lignes = len(grille_du_jeu)
nb_colonnes = len(grille_du_jeu[0])

for y, ligne in enumerate(map1):
    ligne_de_tiles1 = []
    for x, valeur in enumerate(ligne):
        # On passe la position en pixels ET les index x, y de la matrice
        nouvelle_tile = Tile(x*tile_x, y*tile_y, x, y) 
        
        # 1 = mur, 2 = mur_cassable, sinon passage
        if valeur == 1:
            nouvelle_tile.send("build")
        elif valeur == 2:
            nouvelle_tile.send("build_cassable")

        ligne_de_tiles1.append(nouvelle_tile)
        
    grille_du_jeu1.append(ligne_de_tiles1)

bg_original_menu = pygame.image.load(os.path.join('Sprites', 'BG.png')).convert()
bg_original_menu_choix = pygame.image.load(os.path.join('Sprites', 'BG_mode_jeu.png')).convert()

#on charge les backgrounds

# Redimensionnement des images pour avoir la bonne taille
bg_menu = pygame.transform.scale(bg_original_menu, (screen_size_x, screen_size_y))
bg_menu_choix = pygame.transform.scale(bg_original_menu_choix, (screen_size_x, screen_size_y))

#Joueurs
players = [Player(1, 'Joueur 1', 3, player1_pos[0], player1_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE), 
           Player(2, 'Joueur 2', 3, player2_pos[0], player2_pos[1], pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT)]

#IA
AIs = [AI('AI0', 3, AI_pos[0], AI_pos[1]),AI('AI1', 5, AI_pos[0], AI_pos[1]),AI('AI2', 4, AI_pos[0], AI_pos[1]),AI('AI3', 2, AI_pos[0], AI_pos[1]),AI('AI4', 1, AI_pos[0], AI_pos[1])]
AI_active = [AIs[0]]
boss = Boss('boss',3,AI_pos[0], AI_pos[1])

state = 'menu'
clic = False
tap = False
#Joueurs

while running:
#on doit d'abord récupérer les événements depuis le dernier tour. ici on regarde principalement si il y a eu un clic (pour les boutons), et les bombes posées

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            tap = True
            
            for player in players:
                if event.key == player.keybomb and player.est_vivant() and player.bomb_timer <= 0:
                        grille_du_jeu1[int(player.pos_grille[1])][int(player.pos_grille[0])].drop()
                        grille_du_jeu[int(player.pos_grille[1])][int(player.pos_grille[0])].drop()
                        player.bomb_timer += player.BOMB_COOLDOWN
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            tap = True
            clic = True
            clic_posx, clic_posy = pygame.mouse.get_pos()

    if state == 'menu':
        screen.blit(bg_menu,(0,0))
        if tap:
            state = 'menu choix mode de jeu'
        pygame.display.flip()

    elif state == 'menu choix mode de jeu': #pas vraiment des boutons, on regarde si il y a eu un clic (event), et où
        screen.blit(bg_menu_choix,(0,0))
        if clic:
            if clic_posx >=980 and clic_posy <= 70:
                running = False

            elif 630>=clic_posx>=420 and 140<=clic_posy<= 280:
                state = '1v1'

            elif 630>=clic_posx>=420 and 350<=clic_posy<= 490:
                state = 'PVE'

        clic = False
        tap = False
        clic_posx, clic_posy = (0,0)
        
        pygame.display.flip()



    elif state == '1v1': #1 contre 1, on gère un tour de jeu (mais assez rapide pour que ce soit pas en tour par tour)
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

    if state == 'PVE': #on affronte un monstre qui nous court juste dessus
                       
        for ligne in grille_du_jeu1:
            for tile in ligne:
                tile.draw(screen)
                tile.update(dt, grille_du_jeu1)
        
            # Mettre à jour l'affichage de l'écran
        
        keys = pygame.key.get_pressed()
               
        if keys[pygame.K_e]:
            running = False  # Quitter la boucle

        if players[0].est_vivant():
            players[0].show(screen)
            players[0].update(grille_du_jeu1,dt)
            players[0].move(dt, keys, grille_du_jeu1)

        for Ai in AI_active:
            if Ai.est_vivant():
                Ai.show(screen)
                Ai.update(grille_du_jeu1, dt)

        #Mouvement AI (test)
                if (players[0].pos_grille[0],players[0].pos_grille[1]) != (Ai.pos_grille[0],Ai.pos_grille[1]):
                    Ai.moveAI(dt,(players[0].pos_grille[0],players[0].pos_grille[1]),(Ai.pos_grille[0],Ai.pos_grille[1]),grille_du_jeu1) #c'est au point zebi 
                else:
                    players[0].take_damages(1)
            if Ai_spawn_delay == 0 and nb_active_AI < 5:
                Ai_spawn_delay = 5
                AI_active.append(AIs[len(AI_active)])
                nb_active_AI += 1
            else :
                Ai_spawn_delay -= dt
            
            

        #Mettre à jour l'affichage de l'écran
        pygame.display.flip()
        
        # Limite à 60 FPS et calcul du dt (en secondes)
        dt = clock.tick(60) / 1000

    if state == 'boss': #On affronte un boss, qui veut d'abord se mettre en sécurité, puis si possible nous attaquer, et sinon se rapprocher (grâce à dijsktra)
        """Le boss a besoin des cases qui sont soit du feu, soit qui vont le devenir"""
        cases_dangereuses = []
        graphe = creer_graph_boss(grille_du_jeu)
        for ligne in grille_du_jeu:
            for tile in ligne:
                tile.draw(screen)
                tile.update(dt, grille_du_jeu)
                xtile, ytile = tile.x_grid, tile.y_grid
                if tile.current_state == Tile.fire:
                    if (ytile, xtile) not in cases_dangereuses:
                        cases_dangereuses.append((ytile, xtile))

                elif tile.current_state == Tile.bomb:
                    if (ytile, xtile) not in cases_dangereuses:
                        cases_dangereuses.append((ytile, xtile))

                    # On regarde les 4 directions autour de la bombe (portée = 3 cases)
                    portee = 3
                    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        for dist in range(1, portee + 1): # On utilise la même méthode que pour check les directions où la bombe va exploser: on a comme ca les endroits où ca va péter
                            nx = xtile + dx * dist
                            ny = ytile + dy * dist

                            if 0 <= ny < nb_lignes and 0 <= nx < nb_colonnes:
                                # Un mur arrête la flamme. Pas besoin de l'ajouter car il peut pas marcher dessus

                                if grille_du_jeu[ny][nx].current_state == Tile.mur or grille_du_jeu[ny][nx].current_state == Tile.mur_cassable:
                                    break

                                if (ny, nx) not in cases_dangereuses:
                                    cases_dangereuses.append((ny, nx))

        keys = pygame.key.get_pressed()
               
        if keys[pygame.K_e]:
            running = False  # Quitter la boucle

        if boss.est_vivant():
            boss.update(grille_du_jeu, dt)

            # 1. Vérifier s'il y a une bombe ou si ça va péter. Si oui, on fuit
            if boss.est_en_danger(cases_dangereuses):
                boss.fuir(dt, grille_du_jeu, graphe, cases_dangereuses)
            # 2. Sinon, vérifier si le joueur est assez proche. Si oui, le boss pose une bombe
            elif boss.joueur_a_portee(players[0].pos_grille):
                grille_du_jeu[int(boss.pos_grille[1])][int(boss.pos_grille[0])].drop()
                boss.bomb_timer = boss.BOMB_COOLDOWN

            # 3. Sinon -> Se rapprocher du joueur (Dijkstra)
            else:
                boss.se_rapprocher(dt, players[0].pos_grille, grille_du_jeu , graphe, cases_dangereuses)
                print(boss.se_rapprocher(dt, players[0].pos_grille, grille_du_jeu , graphe, cases_dangereuses))
            boss.show(screen)
            
        if players[0].est_vivant():
            players[0].show(screen)
            players[0].update(grille_du_jeu,dt)
            players[0].move(dt, keys, grille_du_jeu)

        #Mettre à jour l'affichage de l'écran
        pygame.display.flip()
        
        # Limite à 60 FPS et calcul du dt (en secondes)
        dt = clock.tick(60) / 1000

pygame.quit()
