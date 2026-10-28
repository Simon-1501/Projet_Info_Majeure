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

    def update(self, dt, grille):
        if self.current_state == Tile.bomb:
            self.timer += dt
            if self.timer >= self.BOMB_DURATION:
                self.declencher_explosion(grille)
                
        elif self.current_state == Tile.fire:
            self.timer += dt
            if self.timer >= self.FIRE_DURATION:
                self.timer = 0
                self.extinguish()

    def declencher_explosion(self, grille):
        # Si la case est déjà en feu, on évite les boucles infinies de réactions en chaîne
        if self.current_state == Tile.fire:
            return None
    
        self.timer = 0
        self.explode()  # Cette case passe à l'état Fire
        
        # Les 4 directions de propagation : (delta_y, delta_x)
        directions = [
            (-1, 0),  # Haut
            (1, 0),   # Bas
            (0, -1),  # Gauche
            (0, 1)    # Droite
        ]
        
        nb_lignes = len(grille)
        nb_colonnes = len(grille[0]) if nb_lignes > 0 else 0

        for dy, dx in directions:
            # On étend le souffle case par case jusqu'à la portée maximale
            for i in range(1, self.range + 1):
                target_y = self.y_grid + (dy * i)
                target_x = self.x_grid + (dx * i)
                
                # Vérification des limites de la carte
                if not (0 <= target_y < nb_lignes and 0 <= target_x < nb_colonnes):
                    break  # Sortie de la carte: stop
                    
                case_cible = grille[target_y][target_x]
                etat_cible = case_cible.current_state
                
                # Cas 1 : Mur incassable: stop
                if etat_cible == Tile.mur:
                    break
                    
                # Cas 2 : Mur cassable: Il prend feu et stoppe le souffle
                elif etat_cible == Tile.mur_cassable:
                    case_cible.explode()
                    break
                    
                # Cas 3 : Une autre bombe
                elif etat_cible == Tile.bomb:
                    # Elle explose tout de suite avec sa propre portée
                    case_cible.declencher_explosion(grille) 
                    break  # Le souffle de la bombe actuelle s'arrête sur elle
                    
                # Cas 4 : Passage libre ou case déjà en feule feu continue
                else:
                    case_cible.explode()

    def draw(self, screen):
        couleurs = {
            "mur": "Grey",
            "mur_cassable": (115, 63, 17),
            "passage": "Green",
            "bomb": "Black",
            "fire": "Red",
        }
        pygame.draw.rect(screen, couleurs[self.current_state.value], self.rect)
