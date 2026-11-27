import pygame
from tile import Tile
import os

class Player:
    """Classe du joueur"""
    """Entité qui peut se déplacer sur la grille. Comme les bombes sont gérées par les cases(statemachine)
    on ne la gère pas ici mais dans les events du main

    Args:
        nom (str): Name identifier. Pas utilisé pour l'instant.
        vie_max (int): Maximum de vie.
        x (int), y (int): coordonées initiales, dans la grille (pas en pixels)
        object (optional): Objet tenu. Pas utilisé pour l'instant.
        keys : les différentes touches de contrôle du joueur.
        color : couleur du joueur (1 ou 2) pour déterminer les sprites à utiliser.

    Attributes:
        sprite1, sprite2, sprite3: On donne la vie des joueurs grâce au sprite (plus ou moins blessé) .
        pos_grille (list): Position sur la grille [x, y].
        pos (Vector2): PPosition en pixels dérivée de la grille.
        Différents timers (bomb, move, damage): contrôle les cooldowns des capacités.
    """
    def __init__(self, color, nom, vie_max, grille_x, grille_y, keyup, keydown, keyleft, keyright, keybomb, object=None):
        self.object = object
        self.nom = nom
        self.vie_max = vie_max
        self.vie = vie_max


        self.degats_recus_ce_tour = False

        if color == 1:
            self.sprite_3 = pygame.image.load(os.path.join('Sprites', 'PLAYER1.png')).convert_alpha()
            self.sprite_3 = pygame.transform.scale(self.sprite_3, (70, 70)) 

            self.sprite_2 = pygame.image.load(os.path.join('Sprites', '2hp.png')).convert_alpha()
            self.sprite_2 = pygame.transform.scale(self.sprite_2, (70, 70)) 

            self.sprite_1 = pygame.image.load(os.path.join('Sprites', '1hp.png')).convert_alpha()
            self.sprite_1 = pygame.transform.scale(self.sprite_1, (70, 70)) 

        else:
            self.sprite_3 = pygame.image.load(os.path.join('Sprites', 'PLAYER2.png')).convert_alpha()
            self.sprite_3 = pygame.transform.scale(self.sprite_3, (70, 70)) 
            
            self.sprite_2 = pygame.image.load(os.path.join('Sprites', '2h2.png')).convert_alpha()
            self.sprite_2 = pygame.transform.scale(self.sprite_2, (70, 70)) 
            
            self.sprite_1 = pygame.image.load(os.path.join('Sprites', '1hp2.png')).convert_alpha()
            self.sprite_1 = pygame.transform.scale(self.sprite_1, (70, 70)) 
            


        self.pos_grille = [grille_x, grille_y]
        self.pos = pygame.Vector2(grille_x*70, grille_y*70)

        self.keyup = keyup
        self.keydown = keydown
        self.keyleft = keyleft
        self.keyright = keyright
        self.keybomb = keybomb

        self.move_timer = 0         # Chronomètre actuel
        self.MOVE_COOLDOWN = 0.2    # Temps d'attente entre deux cases (0.2 seconde)
        self.damage_timer = 1
        self.BOMB_COOLDOWN = 2.5
        self.bomb_timer = 0.25

    def est_vivant(self):
        return self.vie > 0

    def take_damages(self, damages): #Méthode qui gère les dégâts reçus par le joueur. Elle vérifie si le joueur a déjà reçu des dégâts ce tour-ci pour éviter de lui infliger des dégâts multiples en une seule mise à jour.
        if not self.degats_recus_ce_tour : 
            self.vie = max(0, self.vie - damages)
            self.degats_recus_ce_tour = True
            self.damage_timer = 1

    def update(self, grille, dt): #Méthode qui est appelée à chaque frame pour mettre à jour l'état du joueur. Elle gère les timers et vérifie si le joueur est sur une case en feu.
        # Réinitialiser le compteur au début de chaque mise à jour.
        self.degats_recus_ce_tour = 0

        if not self.est_vivant():
            return None

        if self.damage_timer > 0:
            self.damage_timer -= dt

        if self.bomb_timer > 0:
            self.bomb_timer -= dt

            
        x = self.pos_grille[0]
        y = self.pos_grille[1]

        case_actuelle = grille[y][x]

        if case_actuelle.current_state == Tile.fire:
            if self.damage_timer <= 0:
                self.take_damages(1)
                self.damage_timer = 1

    def take_object(self, object):
        self.object = object

    def move(self, dt, keys, grille):
        if self.move_timer > 0:
            self.move_timer -= dt
            if self.move_timer > 0:
                return None
            else:
                self.move_timer = 0

        x_grid = self.pos_grille[0]
        y_grid = self.pos_grille[1]

        nb_lignes = len(grille)
        nb_colonnes = len(grille[0]) if nb_lignes > 0 else 0

        deplacement_effectue = False

        if keys[self.keyup]:
            if y_grid > 0 and grille[y_grid - 1][x_grid].current_state.value in ["fire", "passage"]:
                self.pos_grille[1] -= 1
                deplacement_effectue = True

        elif keys[self.keydown]:
            if y_grid < nb_lignes - 1 and grille[y_grid + 1][x_grid].current_state.value in ["fire", "passage"]:
                self.pos_grille[1] += 1
                deplacement_effectue = True

        elif keys[self.keyleft]:
            if x_grid > 0 and grille[y_grid][x_grid - 1].current_state.value in ["fire", "passage"]:
                self.pos_grille[0] -= 1
                deplacement_effectue = True

        elif keys[self.keyright]:
            if x_grid < nb_colonnes - 1 and grille[y_grid][x_grid + 1].current_state.value in ["fire", "passage"]:
                self.pos_grille[0] += 1
                deplacement_effectue = True

        if deplacement_effectue:
            self.move_timer = self.MOVE_COOLDOWN
            self.pos = pygame.Vector2(self.pos_grille[0]*70, self.pos_grille[1]*70)


    def show(self, screen):
        if self.vie == 3:
            rect_joueur = self.sprite_3.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
            screen.blit(self.sprite_3, rect_joueur)
            
        elif self.vie == 2:
            rect_joueur = self.sprite_2.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
            screen.blit(self.sprite_2, rect_joueur)
            
        elif self.vie == 1:
            rect_joueur = self.sprite_1.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
            screen.blit(self.sprite_1, rect_joueur)