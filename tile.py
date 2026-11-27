import pygame
import os
from statemachine import StateChart, State

class Tile(StateChart):
    """Utilisation d'une state machine pour gérer les états des cases du jeu. 
    Chaque case peut être dans un état différent (mur, passage, bombe, feu, etc.) 
    et les transitions entre ces états sont définies par des événements spécifiques 
    (poser une bombe, explosion, extinction du feu, etc.)."""
    # 1. États
    mur = State("Mur", final=True)
    mur_cassable = State("Mur cassable")
    passage = State("Passage", initial=True)
    bomb = State("Bomb")
    fire = State("Fire")
    fire_laser = State("Fire laser")
    shield = State("Shield")
    
    # 2. Transitions utilisées pour les bombes
    drop = passage.to(bomb)
    explode = bomb.to(fire) | mur_cassable.to(fire) | passage.to(fire) | fire.to(fire) | shield.to(fire)
    lasering = passage.to(fire_laser)
    extinguish = fire.to(passage) | fire_laser.to(passage)


    # 3. Transistions de construction
    build = passage.to(mur)
    build_cassable = passage.to(mur_cassable)
    build_shield = passage.to(shield)

    def __init__(self, x, y, x_grid, y_grid):
        
        super().__init__()
        self.rect = pygame.Rect(x, y, 70, 70)
        
        self.x_grid = x_grid
        self.y_grid = y_grid

        self.range = 3
        self.timer = 0 # Le timer est réinitialisé à 0 pour chaque case, et il est utilisé pour gérer la durée des états "bomb" et "fire". 
                       #Fonctionnement à l'envers par rapport aux bombes (croissant vs décroissant)
        self.hebre_sprite = pygame.image.load(os.path.join('Sprites', 'herbe.png')).convert_alpha()
        self.hebre_sprite = pygame.transform.scale(self.hebre_sprite, (70, 70)) 

        self.shield_sprite = pygame.image.load(os.path.join('Sprites', 'SHIELD.png')).convert_alpha()
        self.shield_sprite = pygame.transform.scale(self.shield_sprite, (70, 70)) 
            
        self.cassable_sprite = pygame.image.load(os.path.join('Sprites', 'cassable.png')).convert_alpha()
        self.cassable_sprite = pygame.transform.scale(self.cassable_sprite, (70, 70)) 

        self.mur_sprite = pygame.image.load(os.path.join('Sprites', 'iron.png')).convert_alpha()
        self.mur_sprite = pygame.transform.scale(self.mur_sprite, (70, 70)) 

        self.bombe_sprite = pygame.image.load(os.path.join('Sprites', 'bomb.png')).convert_alpha()
        self.bombe_sprite = pygame.transform.scale(self.bombe_sprite, (70, 70)) 

        self.fire_sprite = pygame.image.load(os.path.join('Sprites', 'fire.png')).convert_alpha()
        self.fire_sprite = pygame.transform.scale(self.fire_sprite, (70, 70)) 
        
        self.laser_sprite = pygame.image.load(os.path.join('Sprites', 'laser.png')).convert_alpha()
        self.laser_sprite = pygame.transform.scale(self.laser_sprite, (70, 70)) 



        self.laser_arrive = False


        self.LASER_DURATION = 0.75 # 0.75 seconde avant le laser
        self.BOMB_DURATION = 2.0  # 2 secondes avant explosion
        self.FIRE_DURATION = 0.5   # 0.5 seconde de fire
        self.LASER_FIRE_DURATION = 0.1 # 0.1 seconde de fire laser

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
        
        elif self.current_state == Tile.passage and self.laser_arrive:
            if self.timer <= 0:
                self.lasering()
                self.laser_arrive = False
                self.timer = 0
            else:
                self.timer -= dt
        
        elif self.current_state == Tile.fire_laser:
                self.timer = 0
                self.extinguish()


    def declencher_explosion(self,grille):
        """On déclenche l'explosion d'une bombe, en affectant les cases dans les quatre directions (haut, bas, gauche, droite) jusqu'à la portée de l'explosion."""
        # Ne déclencher que les bombes encore actives.
        if self.current_state != Tile.bomb:
            return None

        self.timer = 0
        self.explode()
        directions = [
            (-1, 0),  # Haut
            (1, 0),   # Bas
            (0, -1),  # Gauche
            (0, 1)   # Droite
        ]
        nb_lignes = len(grille)
        nb_colonnes = len(grille[0]) if nb_lignes > 0 else 0

        for dy, dx in directions:
            for i in range(1, self.range + 1):
                target_y = self.y_grid + dy * i
                target_x = self.x_grid + dx * i

                if not (0 < target_y < nb_lignes and 0 < target_x < nb_colonnes):
                    break

                case_cible = grille[target_y][target_x]
                etat_cible = case_cible.current_state

                # Mur incassable : l'explosion s'arrête.
                if etat_cible == Tile.mur :
                    break

                # Une bombe déclenche une réaction en chaîne.
                if etat_cible == Tile.bomb:
                    case_cible.declencher_explosion(grille)
                    break

                # Le souffle touche un passage, un mur cassable ou une case déjà en feu.
                case_cible.explode()
                case_cible.timer = 0

                # Un mur cassable arrête le souffle.
                if etat_cible == Tile.mur_cassable or etat_cible == Tile.shield:
                    break


    def laser_boss(self,laser_duration):
        """Cette fonction est appelée lorsqu'un laser est tiré par le boss. 
        Elle initialise le timer pour la durée du laser et indique que le 
        laser est arrivé sur cette case."""
        self.timer = laser_duration
        self.laser_arrive = True


    def draw(self, screen):
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
        if self.laser_arrive:
            screen.blit(self.laser_sprite,self.rect)



