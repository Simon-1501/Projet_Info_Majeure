import pygame
from statemachine import StateChart, State

class Tile(StateChart):
    # 1. États
    mur = State("Mur", final=True)
    mur_cassable = State("Mur cassable")
    passage = State("Passage", initial=True)
    bomb = State("Bomb")
    fire = State("Fire")
    
    # 2. Transitions
    drop = passage.to(bomb)
    explode = bomb.to(fire) | mur_cassable.to(fire) | passage.to(fire) | fire.to(fire)
    extinguish = fire.to(passage)
    
    build = passage.to(mur)
    build_cassable = passage.to(mur_cassable)

    def __init__(self, x, y, x_grid, y_grid):
        super().__init__()
        self.rect = pygame.Rect(x, y, 70, 70)
        
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.range = 3
        self.timer = 0
        self.BOMB_DURATION = 2.0  # 2 secondes avant explosion
        self.FIRE_DURATION = 0.5   # 0.5 seconde de fire
        self.fire_owners = set()

    def update(self, dt, grille, bomb_owners=None, explosion_events=None):
        if self.current_state == Tile.bomb:
            self.timer += dt

            if self.timer >= self.BOMB_DURATION:
                proprietaire = None

                if bomb_owners is not None:
                    proprietaire = bomb_owners.pop(
                        (self.x_grid, self.y_grid),
                        None,
                    )

                self.declencher_explosion(
                    grille,
                    proprietaire,
                    bomb_owners,
                    explosion_events,
                )

        elif self.current_state == Tile.fire:
            self.timer += dt

            if self.timer >= self.FIRE_DURATION:
                self.timer = 0
                self.extinguish()
                self.fire_owners.clear()

    def declencher_explosion(self,grille,proprietaire=None,bomb_owners=None,explosion_events=None,):
        # Ne déclencher que les bombes encore actives.
        if self.current_state != Tile.bomb:
            return

        self.timer = 0
        self.explode()

        # Enregistrer le propriétaire sur la case de la bombe.
        if proprietaire is not None:
            self.fire_owners.add(proprietaire)

            if explosion_events is not None:
                explosion_events.setdefault(
                    proprietaire, set()
                ).add((self.x_grid, self.y_grid))

        directions = [
            (-1, 0),  # Haut
            (1, 0),   # Bas
            (0, -1),  # Gauche
            (0, 1),   # Droite
        ]

        nb_lignes = len(grille)
        nb_colonnes = len(grille[0]) if nb_lignes > 0 else 0

        for dy, dx in directions:
            for i in range(1, self.range + 1):
                target_y = self.y_grid + dy * i
                target_x = self.x_grid + dx * i

                if not (
                    0 <= target_y < nb_lignes
                    and 0 <= target_x < nb_colonnes
                ):
                    break

                case_cible = grille[target_y][target_x]
                etat_cible = case_cible.current_state

                # Mur incassable : l'explosion s'arrête.
                if etat_cible == Tile.mur:
                    break

                # Une bombe déclenche une réaction en chaîne.
                if etat_cible == Tile.bomb:
                    proprietaire_bombe = None

                    if bomb_owners is not None:
                        proprietaire_bombe = bomb_owners.pop(
                            (target_x, target_y),
                            None,
                        )

                    case_cible.declencher_explosion(
                        grille,
                        proprietaire_bombe,
                        bomb_owners,
                        explosion_events,
                    )

                    break

                # Le souffle touche un passage, un mur cassable
                # ou une case déjà en feu.
                case_cible.explode()
                case_cible.timer = 0

                if proprietaire is not None:
                    case_cible.fire_owners.add(proprietaire)

                    if explosion_events is not None:
                        explosion_events.setdefault(
                            proprietaire, set()
                        ).add((target_x, target_y))

                # Un mur cassable arrête le souffle.
                if etat_cible == Tile.mur_cassable:
                    break

    def draw(self, screen):
        couleurs = {
            "mur": "Grey",
            "mur_cassable": (115, 63, 17),
            "passage": "Green",
            "bomb": "Black",
            "fire": "Red",
        }
        pygame.draw.rect(screen, couleurs[self.current_state.value], self.rect)
