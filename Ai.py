import pygame
from tile import Tile
from Recherche_Boss import *
import os


class AI:
    
    """ On définit cette classe comme un joueur, mais un peu modifié."""
    """Entité de type AI représentant un adversaire qui se comporte comme un joueur

    Args:
        nom (str): Name identifier. Pas utilisé pour l'instant.
        vie_max (int): Maximum de vie.
        x (int), y (int): coordonées initiales.
        object (optional): Objet tenu. Pas utilisé pour l'instant.

    Attributes:
        sprite: Image de l'IA.
        pos_grille (list): Position sur la grille [x, y].
        pos (Vector2): PPosition en pixels dérivée de la grille.
        Différents timers (laser, bomb, move, damage): contrôle les cooldowns des capacités.
    """
    def __init__(self, nom, vie_max, x, y, phase=5, object=None):
        self.object = object
        self.nom = nom
        self.vie_max = vie_max
        self.vie = vie_max


        self.degats_recus_ce_tour = 0

        self.phase = phase

        self.sprite = pygame.image.load(os.path.join('Sprites', 'AI.png')).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (70, 70))         

        self.sprite1 = pygame.image.load(os.path.join('Sprites', 'BOSS1.png')).convert_alpha()
        self.sprite1 = pygame.transform.scale(self.sprite1, (70, 70)) 
        
        self.sprite2 = pygame.image.load(os.path.join('Sprites', 'BOSS2.png')).convert_alpha()
        self.sprite2 = pygame.transform.scale(self.sprite2, (70, 70)) 

        self.sprite3 = pygame.image.load(os.path.join('Sprites', 'BOSS3.png')).convert_alpha()
        self.sprite3 = pygame.transform.scale(self.sprite3, (70, 70)) 

        self.pos_grille = [x, y]
        self.pos = pygame.Vector2(x*70, y*70)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, 40, 50)

        self.LASER_DURATION = 0.75  # 0.75 seconde avant le laser, temps qui peut être modifié
        self.laser_timer = 0
        self.LASER_COOLDOWN = 2.5

        self.move_timer = 0         # Chronomètre actuel
        self.MOVE_COOLDOWN = 0.8*(self.vie_max/3)  # Temps d'attente entre deux cases (0.2 seconde)
        
        if self.MOVE_COOLDOWN <= 0.2:
            self.MOVE_COOLDOWN == 0.25
        self.damage_timer = 0
        
        if self.phase == 2:
            self.vie_max = 1
            self.vie = 1

    def est_vivant(self):
        return self.vie > 0

    def take_damages(self, damages): #inflige damages dégats à l'ia
        vie_avant = self.vie

        self.vie = max(0, self.vie - damages)

        degats_reels = vie_avant - self.vie
        self.degats_recus_ce_tour += degats_reels

    def update(self, grille, dt):
        # Réinitialiser le compteur au début de chaque mise à jour.
        self.degats_recus_ce_tour = 0

        if not self.est_vivant():
            return

        if self.laser_timer > 0:
            self.laser_timer -= dt

        if self.damage_timer > 0:
            self.damage_timer -= dt

        x = int(self.pos_grille[0])
        y = int(self.pos_grille[1])

        case_actuelle = grille[y][x]

        if case_actuelle.current_state == Tile.fire: #inflige un dégat si l'ia est sur une case qui a explosé et réinitialise la durée d'invincibilité
            if self.damage_timer <= 0:
                self.take_damages(1)
                self.damage_timer = 0.6

    def take_object(self, object):
        self.object = object

    def moveAI(self, dt, arrive, depart, grille):
        g = creer_graph_boss(grille)#on crée un graphe adapté à l'état actuel de la grille
        M,p,d = dijkstra(g,depart)#on recherche les chemins les plus courts vers chaque sommet
        Chemin = []
        if arrive not in M: #si on ne peut pas accéder à la position du joueur avec le chemin actuel on recalcule un chemin
            return None
        Chemin = reconstruire_chemin(depart,arrive,p) #on reconstruit un chemin entre la position ia et la position joueur a partir des predecesseurs donnés par dijkstra
        prochaine_case = Chemin[1]
        #On verifie si l'ia a bougé récemment
        if self.move_timer > 0:
            self.move_timer -= dt
            if self.move_timer > 0:
                return None
            else:
                self.move_timer = 0
        #on defini sa position sur la grille du jeu
        x_grid = int(self.pos_grille[0])
        y_grid = int(self.pos_grille[1])

        nb_lignes = len(grille)
        nb_colonnes = len(grille[0]) if nb_lignes > 0 else 0

        deplacement_effectue = False
        #si la prochaine case est a droite de la position
        if prochaine_case[1] > y_grid:
            if y_grid < nb_lignes - 1 and grille[y_grid + 1][x_grid].current_state.value in ["fire", "passage"]:
                self.pos_grille[1] += 1
                deplacement_effectue = True
        #si la prochaine case est a gauche de la position
        elif prochaine_case[1] < y_grid:
            if y_grid > 0 and grille[y_grid - 1][x_grid].current_state.value in ["fire", "passage"]:
                self.pos_grille[1] -= 1
                deplacement_effectue = True
        #si la prochaine case est au dessus de la position
        elif prochaine_case[0] < x_grid:            
            if x_grid > 0 and grille[y_grid][x_grid - 1].current_state.value in [ "passage"]:
                self.pos_grille[0] -= 1
                deplacement_effectue = True 
        #si la prochaine case est au dessous de la position              
        elif prochaine_case[0] > x_grid:
            if x_grid < nb_colonnes - 1 and grille[y_grid][x_grid + 1].current_state.value in [ "passage"]:
                self.pos_grille[0] += 1
                deplacement_effectue = True
        #si l'ia s'est déplacé on attend avant de la redéplacé        
        if deplacement_effectue:
            self.move_timer = self.MOVE_COOLDOWN
            self.pos = pygame.Vector2(self.pos_grille[0]*70, self.pos_grille[1]*70)

    def move_action(self, action, dt, grille):
        """Déplace le joueur selon une action numérique de l'IA."""

        if not self.est_vivant():
            return

        # Gestion du délai entre deux déplacements
        if self.move_timer > 0:
            self.move_timer -= dt

            if self.move_timer > 0:
                return

            self.move_timer = 0

        # Déplacements possibles : dx, dy
        mouvements = {
            0: (0, -1),  # Haut
            1: (0, 1),   # Bas
            2: (-1, 0),  # Gauche
            3: (1, 0),   # Droite
            4: (0, 0),   # Ne rien faire
        }

    

        # L'action 4 = immobilité
        if action == 4:
            return None

        dx, dy = mouvements[action]

        x = int(self.pos_grille[0])
        y = int(self.pos_grille[1])

        cible_x = x + dx
        cible_y = y + dy

        # Vérifier les limites de la grille
        if not (0 <= cible_y < len(grille)):
            return None

        if not (0 <= cible_x < len(grille[0])):
            return None

        # Vérifier si la case est traversable
        etat = grille[cible_y][cible_x].current_state.value

        if etat not in ("fire", "passage"):
            return None

        # Effectuer le déplacement
        self.pos.x = cible_x * 70
        self.pos.y = cible_y * 70

        self.pos_grille = [cible_x, cible_y]

        self.move_timer = self.MOVE_COOLDOWN

    def show(self, screen):
        if self.phase == 0:
            rect_boss = self.sprite1.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
            screen.blit(self.sprite1, rect_boss)

        if self.phase == 1:
            rect_boss = self.sprite2.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
            screen.blit(self.sprite2, rect_boss)

        if self.phase == 2:
            rect_boss = self.sprite3.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
            screen.blit(self.sprite3, rect_boss)

        if self.phase == 5:
            rect_joueur = self.sprite.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
            screen.blit(self.sprite, rect_joueur)
