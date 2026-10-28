import pygame

class Player:
    def __init__(self, sprite, nom, vie_max, x, y, keyup, keydown, keyleft, keyright, keybomb, object=None):
        self.object = object
        self.nom = nom
        self.vie_max = vie_max
        self.vie = vie_max

        self.sprite = sprite
        
        self.pos_grille = [x//70, y//70]
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 40, 50)

        self.keyup = keyup
        self.keydown = keydown
        self.keyleft = keyleft
        self.keyright = keyright
        self.keybomb = keybomb

        self.move_timer = 0         # Chronomètre actuel
        self.MOVE_COOLDOWN = 0.2    # Temps d'attente entre deux cases (0.2 seconde)
        self.damage_timer = 0

    def est_vivant(self):
        if self.vie > 0:
            return True

    def take_damages(self, damages):
        self.vie -= damages
        if self.vie <= 0:
            self.vie = 0

    def update(self, grille, dt):
        if self.damage_timer > 0:
            self.damage_timer -= dt 

        case_actuelle = grille[int(self.pos_grille[1])][int(self.pos_grille[0])]
        
        if case_actuelle.current_state.value == "fire":
            if self.damage_timer <= 0: 
                self.take_damages(1)
                self.damage_timer = 0.6 # Donne 0.6 seconde d'invincibilité 

    def take_object(self, object):
        self.object = object

    def move(self, dt, keys, grille):
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

        if keys[self.keyup]:
            if y_grid > 0 and grille[y_grid - 1][x_grid].current_state.value in ["fire", "passage"]:
                self.pos.y -= 70
                deplacement_effectue = True

        elif keys[self.keydown]:
            if y_grid < nb_lignes - 1 and grille[y_grid + 1][x_grid].current_state.value in ["fire", "passage"]:
                self.pos.y += 70
                deplacement_effectue = True

        elif keys[self.keyleft]:
            if x_grid > 0 and grille[y_grid][x_grid - 1].current_state.value in ["fire", "passage"]:
                self.pos.x -= 70
                deplacement_effectue = True

        elif keys[self.keyright]:
            if x_grid < nb_colonnes - 1 and grille[y_grid][x_grid + 1].current_state.value in ["fire", "passage"]:
                self.pos.x += 70
                deplacement_effectue = True

        if deplacement_effectue:
            self.move_timer = self.MOVE_COOLDOWN
            self.pos_grille = [int(self.pos.x // 70), int(self.pos.y // 70)]

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
