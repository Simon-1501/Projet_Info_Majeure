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

    def show(self, screen):
        rect_joueur = self.sprite.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
        screen.blit(self.sprite, rect_joueur)
