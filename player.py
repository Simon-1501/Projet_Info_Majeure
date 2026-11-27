import pygame
from tile import Tile
import os

class Player:
    """Représente un joueur capable de se déplacer sur la grille et de subir des dégâts.

    Note : La pose et l'explosion des bombes ne sont pas gérées directement ici,
    mais via les événements du fichier principal et la machine à états des cases (Tile).

    Args:
        color (int): Identifiant visuel du joueur (1 ou 2) pour charger les bons sprites.
        nom (str): Nom du joueur (non utilisé pour l'instant).
        vie_max (int): Points de vie maximum au démarrage.
        grille_x (int): Position initiale en colonne sur la grille.
        grille_y (int): Position initiale en ligne sur la grille.
        keyup (int): Touche Pygame pour monter.
        keydown (int): Touche Pygame pour descendre.
        keyleft (int): Touche Pygame pour aller à gauche.
        keyright (int): Touche Pygame pour aller à droite.
        keybomb (int): Touche Pygame pour poser une bombe. Stockée mais non utilisée dans cette classe. Utilisée dans le fichier principal pour déclencher la pose de bombe.
        object (optional): Objet tenu par le joueur (non utilisé pour l'instant).
    """

    def __init__(self, color, nom, vie_max, grille_x, grille_y, keyup, keydown, keyleft, keyright, keybomb, object=None):
        # --- Caractéristiques générales ---
        self.object = object
        self.nom = nom
        self.vie_max = vie_max
        self.vie = vie_max
        self.degats_recus_ce_tour = False  # Verrou pour éviter les dégâts multiples sur une même frame

        # --- Chargement et redimensionnement des sprites selon les PV (70x70 px) ---
        if color == 1:
            self.sprite_3 = pygame.transform.scale(
                pygame.image.load(os.path.join('Sprites', 'PLAYER1.png')).convert_alpha(), (70, 70)
            )
            self.sprite_2 = pygame.transform.scale(
                pygame.image.load(os.path.join('Sprites', '2hp.png')).convert_alpha(), (70, 70)
            )
            self.sprite_1 = pygame.transform.scale(
                pygame.image.load(os.path.join('Sprites', '1hp.png')).convert_alpha(), (70, 70)
            )
        else:
            self.sprite_3 = pygame.transform.scale(
                pygame.image.load(os.path.join('Sprites', 'PLAYER2.png')).convert_alpha(), (70, 70)
            )
            self.sprite_2 = pygame.transform.scale(
                pygame.image.load(os.path.join('Sprites', '2h2.png')).convert_alpha(), (70, 70)
            )
            self.sprite_1 = pygame.transform.scale(
                pygame.image.load(os.path.join('Sprites', '1hp2.png')).convert_alpha(), (70, 70)
            )

        # --- Positionnement ---
        self.pos_grille = [grille_x, grille_y]                     # Coordonnées logiques [colonne, ligne]
        self.pos = pygame.Vector2(grille_x * 70, grille_y * 70)    # Coordonnées d'affichage en pixels

        # --- Configuration des touches ---
        self.keyup = keyup
        self.keydown = keydown
        self.keyleft = keyleft
        self.keyright = keyright
        self.keybomb = keybomb

        # --- Timers et temps de recharge (en secondes) ---
        self.move_timer = 0          # Temps restant avant le prochain déplacement
        self.MOVE_COOLDOWN = 0.2     # Délai minimum entre deux pas
        self.damage_timer = 1        # Temps d'invincibilité restant après un dégât
        self.BOMB_COOLDOWN = 2.5     # Délai minimum entre deux poses de bombe
        self.bomb_timer = 0.25       # Temps restant avant de pouvoir poser une bombe

    def est_vivant(self):
        """Retourne True si le joueur possède encore au moins 1 point de vie."""
        return self.vie > 0

    def take_damages(self, damages):
        """Applique des dégâts au joueur et active son invincibilité temporaire."""
        if not self.degats_recus_ce_tour:
            self.vie = max(0, self.vie - damages)  # Empêche la vie de descendre sous 0
            self.degats_recus_ce_tour = True
            self.damage_timer = 1                  # 1 seconde d'invincibilité

    def update(self, grille, dt):
        """Met à jour les chronomètres et vérifie les dangers sur la case du joueur."""
        self.degats_recus_ce_tour = False

        if not self.est_vivant():
            return None

        # Décrémentation des timers d'invincibilité et de bombe
        if self.damage_timer > 0:
            self.damage_timer -= dt

        if self.bomb_timer > 0:
            self.bomb_timer -= dt

        # Récupération de la case où se trouve actuellement le joueur
        x, y = self.pos_grille[0], self.pos_grille[1]
        case_actuelle = grille[y][x]

        # Inflige 1 dégât si le joueur marche dans le feu (bombe ou laser) et n'est pas invincible
        if case_actuelle.current_state == Tile.fire:
            if self.damage_timer <= 0:
                self.take_damages(1)

    def take_object(self, object):
        """Équipe le joueur avec un objet."""
        self.object = object

    def move(self, dt, keys, grille):
        """Gère le déplacement case par case du joueur selon les touches pressées."""
        # Attente de la fin du cooldown de déplacement
        if self.move_timer > 0:
            self.move_timer -= dt
            if self.move_timer > 0:
                return None
            self.move_timer = 0

        x_grid, y_grid = self.pos_grille[0], self.pos_grille[1]
        nb_lignes = len(grille)
        nb_colonnes = len(grille[0]) if nb_lignes > 0 else 0

        # États de cases sur lesquels le joueur est autorisé à marcher
        cases_franchissables = ["passage", "fire", "fire_laser"]
        deplacement_effectue = False

        # Vérification des directions (Haut, Bas, Gauche, Droite) et des limites de la grille
        if keys[self.keyup]:
            if y_grid > 0 and grille[y_grid - 1][x_grid].current_state.value in cases_franchissables:
                self.pos_grille[1] -= 1
                deplacement_effectue = True

        elif keys[self.keydown]:
            if y_grid < nb_lignes - 1 and grille[y_grid + 1][x_grid].current_state.value in cases_franchissables:
                self.pos_grille[1] += 1
                deplacement_effectue = True

        elif keys[self.keyleft]:
            if x_grid > 0 and grille[y_grid][x_grid - 1].current_state.value in cases_franchissables:
                self.pos_grille[0] -= 1
                deplacement_effectue = True

        elif keys[self.keyright]:
            if x_grid < nb_colonnes - 1 and grille[y_grid][x_grid + 1].current_state.value in cases_franchissables:
                self.pos_grille[0] += 1
                deplacement_effectue = True

        # Mise à jour de la position en pixels et relance du cooldown si le joueur a bougé
        if deplacement_effectue:
            self.move_timer = self.MOVE_COOLDOWN
            self.pos = pygame.Vector2(self.pos_grille[0] * 70, self.pos_grille[1] * 70)

    def show(self, screen):
        """Affiche le sprite correspondant au niveau de vie actuel du joueur."""
        sprites_par_vie = {
            3: self.sprite_3,
            2: self.sprite_2,
            1: self.sprite_1
        }
        sprite_actuel = sprites_par_vie.get(self.vie)
        if sprite_actuel:
            rect_joueur = sprite_actuel.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
            screen.blit(sprite_actuel, rect_joueur)
