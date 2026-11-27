import pygame
import os

# Import des Classes
from player import Player
from tile import Tile
from Ai import AI
from Recherche_Boss import *

#var
tile_x = 70
tile_y = 70
screen_size_x = 1050
screen_size_y = 630

state = 'menu'
clic = False
tap = False

# Position initiale du joueur 
player1_pos = (1,1)
player1_boss_pos = (7,1)
player2_pos = (13,7)
AI_pos = (13,7)
boss_pos =(7,4)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_size_x, screen_size_y))
clock = pygame.time.Clock()
running = True
dt = 0

# Legende : 1 = mur incassable, 2 = mur cassable, 0 = passage
#map 1v1
map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1,0,0,2,2,2,2,2,2,2,2,2,0,0,1], 
       [1,0,1,2,1,1,1,2,1,1,1,2,1,0,1],
       [1,2,2,0,0,0,0,0,0,0,0,0,2,2,1],
       [1,1,2,0,1,0,1,1,1,0,1,0,2,1,1],
       [1,2,2,0,0,0,0,0,0,0,0,0,2,2,1],
       [1,0,1,2,1,1,1,2,1,1,1,2,1,0,1],
       [1,0,0,2,2,2,2,2,2,2,2,2,0,0,1], 
       [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
#map PVE
map1 = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,2,0,0,2,0,2,0,0,2,0,0,1], 
        [1,0,0,0,2,0,0,0,0,0,2,0,0,0,1],
        [1,0,0,0,0,0,2,1,2,0,0,0,0,0,1],
        [1,0,1,2,1,0,1,1,1,0,1,2,1,0,1],
        [1,0,0,0,0,0,2,1,2,0,0,0,0,0,1],
        [1,0,0,0,2,0,0,0,0,0,2,0,0,0,1],
        [1,0,0,2,0,0,2,0,2,0,0,2,0,0,1], 
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]
#map Boss phase 1
mapboss=[[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,2,0,0,2,0,0,0,2,2,0,2,0,1], 
        [1,2,5,2,2,1,0,0,0,1,2,2,5,2,1],
        [1,0,2,0,2,0,1,1,1,0,2,0,2,0,1],
        [1,0,1,2,1,0,1,0,1,0,1,2,1,0,1],
        [1,0,2,0,2,0,1,1,1,0,2,0,2,0,1],
        [1,2,5,2,2,1,0,0,0,1,2,2,5,2,1],
        [1,0,2,0,0,0,2,2,2,0,0,0,2,0,1], 
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

mapboss2=[[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1], 
        [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,0,1,0,0,0,0,0,1,0,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1], 
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

# creation grille de jeu

codes_terrain = {Tile.passage: 0,
                 Tile.mur: 1,
                 Tile.mur_cassable: 2,
                 Tile.bomb: 3,
                 Tile.fire: 4,
                 Tile.shield: 5
                 }
'''On utilise une statemachine pour la grille, on doit donc créer les Tiles, 
puis les faire évoluer grâce aux transitions de la statemachine.
La grille créée est une matrice de Tile, chaque Tile ayant un état (passage, mur, mur cassable, bombe, feu, bouclier).
Pour parcourir la '''
def creer_grille(map):
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
            elif valeur == 5:
                nouvelle_tile.send("build_shield")

            ligne_de_tiles.append(nouvelle_tile)
            
        grille_du_jeu.append(ligne_de_tiles)
    return grille_du_jeu

grille_du_jeu = creer_grille(map)
grille_du_jeu1 = creer_grille(map1)


bg_original_menu = pygame.image.load(os.path.join('Sprites', 'BG.png')).convert()
bg_original_menu_choix = pygame.image.load(os.path.join('Sprites', 'BG_mode_jeu.png')).convert()
bg_original_victory = pygame.image.load(os.path.join('Sprites', 'victory.png')).convert()
bg_original_jeux = pygame.image.load(os.path.join('Sprites', 'BGgame.png')).convert()
#on charge les backgrounds

# Redimensionnement des images pour avoir la bonne taille
bg_menu = pygame.transform.scale(bg_original_menu, (screen_size_x, screen_size_y))
bg_menu_choix = pygame.transform.scale(bg_original_menu_choix, (screen_size_x, screen_size_y))
bg_victory = pygame.transform.scale(bg_original_victory, (screen_size_x, screen_size_y))
bg_jeux = pygame.transform.scale(bg_original_jeux, (screen_size_x, screen_size_y))


clic = False
tap = False
#Joueurs
players = [Player(1, 'Joueur 1', 3, player1_pos[0], player1_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE), 
           Player(2, 'Joueur 2', 3, player2_pos[0], player2_pos[1], pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT)]


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

    keys = pygame.key.get_pressed()

    if keys[pygame.K_t]: #Ouvre le mode test : afficher le chemin de l'ia + ia qui ne fait pas de dégats
        state = 'Test'
        Ai = AI('AI0', 3, AI_pos[0], AI_pos[1])
        players[0] = Player(1, 'Joueur 1', 3, player1_pos[0], player1_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE)
        pause = False
        grille_du_jeu = creer_grille(map1)

    if keys[pygame.K_m]:
        state = 'menu' # Rammene au menu

    if keys[pygame.K_e]:
        running = False  # Quitter la boucle

    if state == 'menu':
        screen.blit(bg_menu,(0,0)) 

        if tap:
            state = 'menu choix mode de jeu'
        pygame.display.flip()
    
    if state == 'victory': #ecran de victoire
        screen.blit(bg_victory,(0,0)) 
        if clic:
            state = 'menu choix mode de jeu'
        pygame.display.flip()

    elif state == 'menu choix mode de jeu': #pas vraiment des boutons, on regarde si il y a eu un clic (event), et où
        screen.blit(bg_menu_choix,(0,0))
        if clic:
            if clic_posx >=910 and clic_posy <= 70: #si on clique sur la fleche ça ferme le jeu 
                running = False

            elif 630>=clic_posx>=420 and 140<=clic_posy<= 280: #si on clique sur le bouton 1v1 on lance le mode 1v1
                state = '1v1'
                players = [Player(1, 'Joueur 1', 3, player1_pos[0], player1_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE), Player(2, 'Joueur 2', 3, player2_pos[0], player2_pos[1], pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT)]
                grille_du_jeu = creer_grille(map)

            elif 630>=clic_posx>=420 and 350<=clic_posy<= 490: #si on clique sur le bouton VSIA on lance le mode PVE
                state = 'PVE'
                AIs = [AI('AI0', 3, AI_pos[0], AI_pos[1]),AI('AI1', 5, AI_pos[0], AI_pos[1]),AI('AI2', 4, AI_pos[0], AI_pos[1]),AI('AI3', 2, AI_pos[0], AI_pos[1]),AI('AI4', 5, AI_pos[0], AI_pos[1])]
                AI_active = [AIs[0]]
                grille_du_jeu1 = creer_grille(map1)
                Ai_spawn_delay = 15 #delay d'apparition de la seconde ia en PVE en secondes
                nb_active_AI = 1
                grille_du_jeu = creer_grille(mapboss)

        clic = False
        tap = False
        clic_posx, clic_posy = (0,0)
        
        pygame.display.flip()

    elif state == '1v1': #1 contre 1, on gère un tour de jeu (mais assez rapide pour que ce soit pas en tour par tour)
        screen.blit(bg_jeux,(0,0)) 

        for ligne in grille_du_jeu:
            for tile in ligne:
                tile.draw(screen)
                tile.update(dt, grille_du_jeu)

    # Mettre à jour l'affichage de l'écran
        compteur_vivant = 0
        # Joueurs
        for player in players:
            if player.est_vivant():
                compteur_vivant += 1
                player.update(grille_du_jeu, dt)
                player.move(dt,keys,grille_du_jeu)
                player.show(screen)

        if compteur_vivant <= 1: #quand un joueur est éliminé on affiche l'écran de victoire
            state = 'victory'
            grille_du_jeu1 = creer_grille(map1)
            grille_du_jeu = creer_grille(map)
            players = [Player(1, 'Joueur 1', 3, player1_pos[0], player1_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE), 
           Player(2, 'Joueur 2', 3, player2_pos[0], player2_pos[1], pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT)]
        '''On doit réinitialiser les joueurs et la grille de jeu pour que le joueur puisse rejouer, sinon il resterait mort et la grille serait dans l'état où elle était à la fin de la partie'''

        # Mettre à jour l'affichage de l'écran
        pygame.display.flip()

        # Limite à 60 FPS et calcul du dt (en secondes)
        dt = clock.tick(60) / 1000

    elif state == 'PVE': #on affronte des monstres qui nous court juste dessus, puis le boss si on les bat tous
        screen.blit(bg_jeux,(0,0)) 
         
        for ligne in grille_du_jeu1:
            for tile in ligne:
                tile.draw(screen)
                tile.update(dt, grille_du_jeu1)
        
            # Mettre à jour l'affichage de l'écran

        players[0].degats_recus_ce_tour = False

        if players[0].est_vivant():#tant que le joueur est vivant  on met a jour son état, sa position et on l'affiche
            players[0].show(screen)
            players[0].update(grille_du_jeu1,dt)
            players[0].move(dt, keys, grille_du_jeu1)
        else:
            state = 'menu choix mode de jeu'
            players = [Player(1, 'Joueur 1', 3, player1_pos[0], player1_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE), 
           Player(2, 'Joueur 2', 3, player2_pos[0], player2_pos[1], pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT)]


        vivant = False
        for Ai in AI_active:
            if Ai.est_vivant():
                vivant = True #tant qu'au moins une IA est vivante 
                Ai.show(screen)
                Ai.update(grille_du_jeu1, dt)

        #Mouvement AI
                if (players[0].pos_grille[0],players[0].pos_grille[1]) != (Ai.pos_grille[0],Ai.pos_grille[1]): #si la position de l'ia est différente de la position du joueur elle cherche un chemin
                    Ai.moveAI(dt,(players[0].pos_grille[0],players[0].pos_grille[1]),(Ai.pos_grille[0],Ai.pos_grille[1]),grille_du_jeu1) 
                else:# si l'ia est sur le joueuret qu'il n'a pas reçu de dégats depuis une seconde le joueur prend un dégat
                    if players[0].damage_timer <= 0:
                        players[0].take_damages(1)

        if Ai_spawn_delay <= 0 and nb_active_AI < 5: #si le delay d'apparition est passé et que toutes les ia ne sont pas encore apparus on en fait apparaite une de plus
            Ai_spawn_delay = 30
            AI_active.append(AIs[len(AI_active)])
            nb_active_AI += 1

        else : #sinon on fait diminuer le delay d'apparition
            Ai_spawn_delay -= dt

        if (not vivant and nb_active_AI >= 5) or keys[pygame.K_b]: #si toutes les ia sont éliminé on passe au boss et on réinitialise le joueur
            state = 'boss'
            players = [Player(1, 'Joueur 1', 3, player1_boss_pos[0], player1_boss_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE)]
            boss = AI('boss',3,boss_pos[0], boss_pos[1],0)
            

        #Mettre à jour l'affichage de l'écran
        pygame.display.flip()
        
        # Limite à 60 FPS et calcul du dt (en secondes)
        dt = clock.tick(60) / 1000

    elif state == 'boss': #On affronte un boss, qui veut d'abord se mettre en sécurité, puis si possible nous attaquer, et sinon se rapprocher (grâce à dijsktra)
        """Le boss est constitué de 2 phases, une où on doit détruire ses 4  boucliers, puis une où il nous cours dessus"""
        screen.blit(bg_jeux,(0,0)) 
        
        cases_dangereuses = []
        nb_lignes = len(grille_du_jeu)
        nb_colonnes = len(grille_du_jeu[0])
        compteur_shield = 0
        for ligne in grille_du_jeu:
            for tile in ligne:
                tile.draw(screen)
                tile.update(dt, grille_du_jeu)
                xtile, ytile = tile.x_grid, tile.y_grid
                
                if tile.current_state == Tile.fire:
                    if (ytile, xtile) not in cases_dangereuses:
                        cases_dangereuses.append((ytile, xtile))

                elif tile.current_state == Tile.shield:
                    compteur_shield += 1

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

        if 0<compteur_shield <= 2 or keys[pygame.K_o]:
            boss.LASER_DURATION = 0.5
            boss.LASER_COOLDOWN = 1.5
            boss.phase = 1

        #On gangne lorsque le boss n'a plus de bouclier
        if compteur_shield > 0:
            boss.update(grille_du_jeu, dt)
            boss.show(screen)

            if boss.laser_timer <= 0:
                boss.laser_timer = boss.LASER_COOLDOWN
                tile_joueur = grille_du_jeu[int(players[0].pos_grille[1])][int(players[0].pos_grille[0])]
                tile_joueur.laser_boss(boss.LASER_DURATION)
        
        if compteur_shield == 0 or keys[pygame.K_p]:
            boss = AI('AI0', 1.5,boss_pos[0] , boss_pos[1],2)
            state = 'phase finale'
            grille_du_jeu = creer_grille(mapboss2)
            
        if players[0].est_vivant():
            players[0].show(screen)
            players[0].update(grille_du_jeu,dt)
            players[0].move(dt, keys, grille_du_jeu)

        else:
            state = 'menu choix mode de jeu'
            players = [Player(1, 'Joueur 1', 3, player1_pos[0], player1_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE), 
           Player(2, 'Joueur 2', 3, player2_pos[0], player2_pos[1], pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT)]


        #Mettre à jour l'affichage de l'écran
        pygame.display.flip()
        
        # Limite à 60 FPS et calcul du dt (en secondes)
        dt = clock.tick(60) / 1000

    # 'phase finale' state: Il s'agit de la phase finale du combat contre le boss ; elle se déclenche lorsque le boss perd tous ses boucliers, ou en appuyant sur la touche « p » alors que l'on se trouve dans l'état « boss ».

    elif state == 'phase finale':
        screen.blit(bg_jeux,(0,0)) 
        screen.blit(bg_jeux,(0,0)) 

        for ligne in grille_du_jeu:
            for tile in ligne:
                tile.draw(screen)
                tile.update(dt, grille_du_jeu)
                
                # Mettre à jour l'affichage de l'écran

        if players[0].est_vivant():
            players[0].show(screen)
            players[0].update(grille_du_jeu,dt)
            players[0].move(dt, keys, grille_du_jeu)
        else:
            state = 'menu choix mode de jeu'
            players = [Player(1, 'Joueur 1', 3, player1_pos[0], player1_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE), 
           Player(2, 'Joueur 2', 3, player2_pos[0], player2_pos[1], pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT)]
        

        if boss.est_vivant():
            
            boss.show(screen)
            boss.update(grille_du_jeu,dt)

            if (players[0].pos_grille[0],players[0].pos_grille[1]) != (boss.pos_grille[0],boss.pos_grille[1]): #si la position de l'ia est différente de la position du joueur elle cherche un chemin
                boss.moveAI(dt,(players[0].pos_grille[0],players[0].pos_grille[1]),(boss.pos_grille[0],boss.pos_grille[1]),grille_du_jeu) 
            
            else:# si l'ia est sur le joueuret qu'il n'a pas reçu de dégats depuis une seconde le joueur prend un dégat
                if players[0].damage_timer <= 0:
                    players[0].take_damages(3)    

        else:
            state = 'victory'
            players = [Player(1, 'Joueur 1', 3, player1_pos[0], player1_pos[1], pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d, pygame.K_SPACE), 
           Player(2, 'Joueur 2', 3, player2_pos[0], player2_pos[1], pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT)]

        pygame.display.flip()
        
        # Limite à 60 FPS et calcul du dt (en secondes)
        dt = clock.tick(60) / 1000


    if state == 'Test':
        screen.blit(bg_jeux,(0,0)) 

        for ligne in grille_du_jeu1:
            for tile in ligne:
                tile.draw(screen)
                tile.update(dt, grille_du_jeu1)
                
                # Mettre à jour l'affichage de l'écran

        if keys[pygame.K_r] :
            pause = not pause

        if players[0].est_vivant():
            players[0].show(screen)
            players[0].update(grille_du_jeu1,dt)
            players[0].move(dt, keys, grille_du_jeu1)

        if Ai.est_vivant():
            Ai.show(screen)
            Ai.update(grille_du_jeu1,dt)
        if not pause:
            if (players[0].pos_grille[0],players[0].pos_grille[1]) != (Ai.pos_grille[0],Ai.pos_grille[1]):
                Ai.moveAI(dt,(players[0].pos_grille[0],players[0].pos_grille[1]),(Ai.pos_grille[0],Ai.pos_grille[1]),grille_du_jeu1)

        g = creer_graph_boss(grille_du_jeu1)
        M,p,d = dijkstra(g,(Ai.pos_grille[0],Ai.pos_grille[1]))
        if (players[0].pos_grille[0],players[0].pos_grille[1]) in M:
            Chemin = reconstruire_chemin((Ai.pos_grille[0],Ai.pos_grille[1]),(players[0].pos_grille[0],players[0].pos_grille[1]),p)
            for case in Chemin[1:-1]:
                pygame.draw.rect(screen,'blue',(case[0]*70,case[1]*70,60,60))
        #Mettre à jour l'affichage de l'écran
        pygame.display.flip()
                
        # Limite à 60 FPS et calcul du dt (en secondes)
        dt = clock.tick(60) / 1000
        
pygame.quit()
