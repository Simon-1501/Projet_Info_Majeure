import pygame
from tile import Tile
from Recherche_Boss import *
import os

class Boss:
    """ On définit cette classe comme un joueur, mais un peu modifié. On a comme méthodes"""
    def __init__(self, nom, vie_max, x, y, object=None):
        self.object = object
        self.nom = nom
        self.vie_max = vie_max
        self.vie = vie_max

        self.phase = 1

        self.degats_recus_ce_tour = 0

        self.sprite = pygame.image.load(os.path.join('Sprites', 'PLAYER2.png')).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (70, 70)) 
            

        self.pos_grille = [x, y]
        self.pos = pygame.Vector2(x*70, y*70)


        self.laser_timer = 0
        self.LASER_COOLDOWN = 2
        self.move_timer = 0
        self.MOVE_COOLDOWN = 0.5
        self.damage_timer = 0
        self.bomb_timer = 0
        self.BOMB_COOLDOWN = 3.0    # Temps d'attente entre deux poses de bombe
        self.portee_bombe = 3       # Distance en cases pour poser une bombe

    def est_vivant(self):
        return self.vie > 0

    def take_damages(self, damages):
        vie_avant = self.vie
        self.vie = max(0, self.vie - damages)
        degats_reels = vie_avant - self.vie
        self.degats_recus_ce_tour += degats_reels

    def update(self, grille, dt):
        self.degats_recus_ce_tour = 0

        if not self.est_vivant():
            return

        if self.laser_timer > 0:
            self.laser_timer -= dt

        if self.damage_timer > 0:
            self.damage_timer -= dt

        if self.bomb_timer > 0:
            self.bomb_timer -= dt

        x = int(self.pos_grille[0])
        y = int(self.pos_grille[1])

        case_actuelle = grille[y][x]

        if case_actuelle.current_state == Tile.fire:
            if self.damage_timer <= 0:
                self.take_damages(1)
                self.damage_timer = 2


    """On a maintenant les méthodes spécifiques"""
    # Vérifier s'il y a une bombe
    def est_en_danger(self, cases_dangereuses):
        pos_actuelle = (int(self.pos_grille[0]), int(self.pos_grille[1]))  # (ligne, col)
        return pos_actuelle in cases_dangereuses

    def fuir(self, dt, grille, cases_dangereuses):
        if self.move_timer > 0:
            self.move_timer -= dt
            return False
        
        graphe = creer_graph_boss(grille)
        depart = (int(self.pos_grille[0]),int(self.pos_grille[1]))

        case_sure, parents = recherche_largeur(depart, graphe, cases_dangereuses)
        print('sur',case_sure)
        """On regarde les voisins de la case de départ, et on enchaine jusqu'à tomber sur une case sure (ou avoir exploré tous les voisins)"""
        
        if case_sure is not None and case_sure != depart:
            chemin = reconstruire_chemin(depart, case_sure, parents)
            if len(chemin) > 0:
                if chemin[0] == depart:
                    prochaine_case = chemin[1]
                print('chemin', chemin, 'pro case', prochaine_case)

                self.bouger_proche(prochaine_case, dt, grille)

                

    #Vérifier si le joueur est assez proche
    def joueur_a_portee(self, pos_joueur, grille):
        """
        Vérifie si le joueur est aligné avec le boss, à portée d'explosion,
        et qu'aucun mur ne bloque la flamme entre eux
        """
        if self.bomb_timer > 0:
            return False

        x_boss, y_boss = int(self.pos_grille[0]), int(self.pos_grille[1])
        x_joueur, y_joueur = int(pos_joueur[0]), int(pos_joueur[1])

        # 1. Le joueur doit être sur la même ligne ou la même colonne
        if x_boss != x_joueur and y_boss != y_joueur:
            return False

        # 2. Vérifier la distance
        distance = abs(x_boss - x_joueur) + abs(y_boss - y_joueur)
        if distance > self.portee_bombe:
            return False

        # 3. Vérifier qu'il n'y a pas de mur entre le boss et le joueur
        if x_boss == x_joueur:  # Même colonne
            if y_joueur > y_boss:
                dx = 1
            else:
                dx = -1
            for y in range(y_boss + dx, y_joueur, dx):
                if grille[y][x_boss].current_state.value in ["mur", "mur_cassable"]:
                    return False

        elif y_boss == y_joueur:  # Même ligne
            if x_joueur > x_boss:
                dy = 1
            else:
                dy = -1
            for x in range(x_boss + dy, x_joueur, dy):
                if grille[y_boss][x].current_state.value in ["mur", "mur_cassable"]:
                    return False

        return True


    def peut_poser_bombe(self):
        """Réinitialise le timer quand le boss pose une bombe dans le main."""
        self.bomb_timer = self.BOMB_COOLDOWN

   
    
    def se_rapprocher(self, dt, arrive, grille, cases_dangereuses):
        arrive = (int(arrive[0]),int(arrive[1]))
        depart = (int(self.pos_grille[0]),int(self.pos_grille[1]))
        g = creer_graph_boss(grille)
        M,p,d = dijkstra(g,depart)
        Chemin = []
        if arrive not in M:
            return None
        
        Chemin = reconstruire_chemin(depart,arrive,p)
        
        if Chemin[0] == depart:
            prochaine_case = Chemin[1]

        if prochaine_case in cases_dangereuses:
            return None
        self.bouger_proche(prochaine_case, dt, grille, )


    def bouger_proche(self,prochaine_case,dt,grille):
        if self.move_timer > 0:
            self.move_timer -= dt
            if self.move_timer > 0:
                return None
            else:
                self.move_timer = 0

        x_grid = int(self.pos_grille[0])
        y_grid = int(self.pos_grille[1])

        nb_lignes = len(grille)
        nb_colonnes = len(grille[0]) if nb_lignes > 0 else 0

        deplacement_effectue = False


        if prochaine_case[1] > y_grid:
            if y_grid < nb_lignes - 1 and grille[y_grid + 1][x_grid].current_state.value in ["fire", "passage"]:
                self.pos_grille[1] += 1
                deplacement_effectue = True

        elif prochaine_case[1] < y_grid:
            if y_grid > 0 and grille[y_grid - 1][x_grid].current_state.value in ["fire", "passage"]:
                self.pos_grille[1] -= 1
                deplacement_effectue = True

        elif prochaine_case[0] < x_grid:
            if x_grid > 0 and grille[y_grid][x_grid - 1].current_state.value in [ "passage"]:
                self.pos_grille[0] -= 1
                deplacement_effectue = True        

        elif prochaine_case[0] > x_grid:
            if x_grid < nb_colonnes - 1 and grille[y_grid][x_grid + 1].current_state.value in [ "passage"]:
                self.pos_grille[0] += 1
                deplacement_effectue = True
                
                

        if deplacement_effectue:
            self.move_timer = self.MOVE_COOLDOWN
            self.pos = pygame.Vector2(self.pos_grille[0]*70, self.pos_grille[1]*70)



    def show(self, screen):
        rect_boss = self.sprite.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
        screen.blit(self.sprite, rect_boss)
