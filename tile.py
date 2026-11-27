import pygame
import os
from statemachine import StateChart, State

class Tile(StateChart):
    """Représente une case de la grille gérée par une machine à états (StateChart).

    Chaque case évolue entre différents états (passage, mur, bombe, feu, bouclier, laser)
    et déclenche des transitions selon les interactions du jeu (pose de bombe, explosion,
    attaque du boss, extinction).

    Args:
        x (int): Position horizontale d'affichage en pixels.
        y (int): Position verticale d'affichage en pixels.
        x_grid (int): Coordonnée de colonne dans la grille logique.
        y_grid (int): Coordonnée de ligne dans la grille logique.
    """

    # --- 1. Définition des états possibles d'une case ---
    mur = State("Mur", final=True)            # Mur indestructible (état terminal)
    mur_cassable = State("Mur cassable")      # Obstacle destructible par une explosion
    passage = State("Passage", initial=True)  # Case libre par défaut
    bomb = State("Bomb")                      # Case contenant une bombe amorcée
    fire = State("Fire")                      # Case enflammée par une bombe
    fire_laser = State("Fire laser")          # Case enflammée par le laser du boss
    shield = State("Shield")                  # Bouclier du boss (destructible par bombe)

    # --- 2. Transitions liées aux explosions et au laser ---
    drop = passage.to(bomb)
    explode = (
        bomb.to(fire)
        | mur_cassable.to(fire)
        | passage.to(fire)
        | fire.to(fire)
        | shield.to(fire)
    )
    lasering = passage.to(fire_laser)
    extinguish = fire.to(passage) | fire_laser.to(passage)

    # --- 3. Transitions de construction (génération de la carte) ---
    build = passage.to(mur)
    build_cassable = passage.to(mur_cassable)
    build_shield = passage.to(shield)

    def __init__(self, x, y, x_grid, y_grid):
        super().__init__()

        # --- Positionnement graphique et logique ---
        self.rect = pygame.Rect(x, y, 70, 70)
        self.x_grid = x_grid
        self.y_grid = y_grid

        # --- Paramètres d'explosion et chronomètre ---
        self.range = 3   # Portée de l'explosion en nombre de cases
        self.timer = 0   # Chronomètre polyvalent (croissant pour bomb/fire, décroissant pour laser)

        # --- Chargement et redimensionnement des textures (70x70 px) ---
        self.hebre_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join('Sprites', 'herbe.png')).convert_alpha(), (70, 70)
        )
        self.shield_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join('Sprites', 'SHIELD.png')).convert_alpha(), (70, 70)
        )
        self.cassable_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join('Sprites', 'cassable.png')).convert_alpha(), (70, 70)
        )
        self.mur_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join('Sprites', 'iron.png')).convert_alpha(), (70, 70)
        )
        self.bombe_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join('Sprites', 'bomb.png')).convert_alpha(), (70, 70)
        )
        self.fire_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join('Sprites', 'fire.png')).convert_alpha(), (70, 70)
        )
        self.laser_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join('Sprites', 'laser.png')).convert_alpha(), (70, 70)
        )

        # --- Indicateur et durées des états temporaires (en secondes) ---
        self.laser_arrive = False      # True lorsqu'un tir laser cible cette case
        self.LASER_DURATION = 0.75     # Temps de prévisualisation avant l'impact du laser
        self.BOMB_DURATION = 2.0       # Délai avant l'explosion d'une bombe
        self.FIRE_DURATION = 0.5       # Durée des flammes d'une bombe
        self.LASER_FIRE_DURATION = 0.1 # Durée des flammes du laser

    def update(self, dt, grille):
        """Met à jour le chronomètre de la case et déclenche les transitions temporelles."""
        # 1. Compte à rebours avant explosion de la bombe
        if self.current_state == Tile.bomb:
            self.timer += dt
            if self.timer >= self.BOMB_DURATION:
                self.declencher_explosion(grille)

        # 2. Durée de persistance du feu classique
        elif self.current_state == Tile.fire:
            self.timer += dt
            if self.timer >= self.FIRE_DURATION:
                self.timer = 0
                self.extinguish()

        # 3. Prévisualisation du laser du boss avant l'impact
        elif self.current_state == Tile.passage and self.laser_arrive:
            if self.timer <= 0:
                self.lasering()
                self.laser_arrive = False
                self.timer = 0
            else:
                self.timer -= dt

        # 4. Durée d'activité du feu généré par le laser
        elif self.current_state == Tile.fire_laser:
            self.timer += dt
            if self.timer >= self.LASER_FIRE_DURATION:
                self.timer = 0
                self.extinguish()

    def declencher_explosion(self, grille):
        """Propage l'explosion de la bombe en croix (haut, bas, gauche, droite)."""
        # Sécurité : empêche de déclencher une case qui n'est plus une bombe
        if self.current_state != Tile.bomb:
            return None

        self.timer = 0
        self.explode()  # La case d'origine passe en état "fire"

        directions = [
            (-1, 0),  # Haut
            (1, 0),   # Bas
            (0, -1),  # Gauche
            (0, 1)    # Droite
        ]
        nb_lignes = len(grille)
        nb_colonnes = len(grille[0]) if nb_lignes > 0 else 0

        # Propagation du souffle dans chacune des 4 directions
        for dy, dx in directions:
            for i in range(1, self.range + 1):
                target_y = self.y_grid + dy * i
                target_x = self.x_grid + dx * i

                # Vérification des limites intérieures de la grille
                if not (0 < target_y < nb_lignes and 0 < target_x < nb_colonnes):
                    break

                case_cible = grille[target_y][target_x]
                etat_cible = case_cible.current_state

                # Un mur indestructible bloque totalement l'explosion
                if etat_cible == Tile.mur:
                    break

                # Réaction en chaîne : fait exploser immédiatement une autre bombe touchée
                if etat_cible == Tile.bomb:
                    case_cible.declencher_explosion(grille)
                    break

                # Enflamme la case cible (passage, mur cassable, bouclier ou feu existant)
                case_cible.explode()
                case_cible.timer = 0

                # Un obstacle destructible (mur cassable ou bouclier) absorbe le souffle
                if etat_cible == Tile.mur_cassable or etat_cible == Tile.shield:
                    break

    def laser_boss(self, laser_duration):
        """Prépare la case à recevoir un tir laser du boss après un délai donné."""
        self.timer = laser_duration
        self.laser_arrive = True

    def draw(self, screen):
        """Affiche la texture correspondant à l'état actuel de la case (et le viseur laser)."""
        sprite = {
            "mur": self.mur_sprite,
            "mur_cassable": self.cassable_sprite,
            "passage": self.hebre_sprite,
            "bomb": self.bombe_sprite,
            "fire": self.fire_sprite,
            "shield": self.shield_sprite,
            "fire_laser": self.fire_sprite
        }

        screen.blit(sprite[self.current_state.value], self.rect)

        # Superpose l'indicateur de visée si un laser est sur le point de frapper
        if self.laser_arrive:
            screen.blit(self.laser_sprite, self.rect)
