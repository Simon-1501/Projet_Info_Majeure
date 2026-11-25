import pygame
from tile import Tile
from Recherche import *


class AI:
    def __init__(self, sprite, nom, vie_max, x, y, object=None):
        self.object = object
        self.nom = nom
        self.vie_max = vie_max
        self.vie = vie_max


        self.degats_recus_ce_tour = 0

        self.sprite = sprite
        
        self.pos_grille = [x, y]
        self.pos = pygame.Vector2(x*70, y*70)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, 40, 50)


        self.move_timer = 0         # Chronomètre actuel
        self.MOVE_COOLDOWN = 0.5    # Temps d'attente entre deux cases (0.2 seconde)
        self.damage_timer = 0

    def est_vivant(self):
        return self.vie > 0

    def take_damages(self, damages):
        vie_avant = self.vie

        self.vie = max(0, self.vie - damages)

        degats_reels = vie_avant - self.vie
        self.degats_recus_ce_tour += degats_reels

    def update(self, grille, dt):
        # Réinitialiser le compteur au début de chaque mise à jour.
        self.degats_recus_ce_tour = 0

        if not self.est_vivant():
            return

        if self.damage_timer > 0:
            self.damage_timer -= dt

        x = int(self.pos_grille[0])
        y = int(self.pos_grille[1])

        case_actuelle = grille[y][x]

        if case_actuelle.current_state == Tile.fire:
            if self.damage_timer <= 0:
                self.take_damages(1)
                self.damage_timer = 0.6

    def take_object(self, object):
        self.object = object

    def moveAI(self, dt, arrive, depart, grille):

        p = dijkstra(grille,depart)[1]
        Chemin = reconstruire_chemin(depart,arrive,p)
        prochaine_case = Chemin[1]
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
            print("a")
            if x_grid > 0 and grille[y_grid][x_grid - 1].current_state.value in [ "passage"]:
                self.pos_grille[0] -= 1
                deplacement_effectue = True               
        elif prochaine_case[0] > x_grid:
            if x_grid < nb_colonnes - 1 and grille[y_grid][x_grid + 1].current_state.value in [ "passage"]:
                self.pos_grille[0] += 1
                deplacement_effectue = True
                print("b")
                

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
        rect_joueur = self.sprite.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
        screen.blit(self.sprite, rect_joueur)
