import pygame
from tile import Tile

class Bomb:
    def __init__(self, x, y, damage = 1, range_b = 3):
        self.damage = damage
        self.range = range_b
        self.x = (x//70)*70
        self.y = (y//70)*70
        self.rect = pygame.Rect((self.x,self.y),(70,70))
        self.temps_creation = pygame.time.get_ticks()
        self.delai_explosion = 2000  
        self.duree_explosion = 500  
        self.etat = "attente"        # possible: "attente", "explosion" ou "detruite"
        self.zones_explosion = [self.rect]    # les zones qui vont péter

    def update(self, grille_du_jeu):
        temps_actuel = pygame.time.get_ticks()
        if self.etat == "attente" and (temps_actuel - self.temps_creation >= self.delai_explosion):
            self.etat = "explosion"
            self.temps_explosion = temps_actuel            
            self.calculer_et_casser_murs(grille_du_jeu)

        elif self.etat == "explosion" and (temps_actuel - self.temps_explosion >= self.duree_explosion):
            self.etat = "detruite"

    def calculer_et_casser_murs(self, grille):
        directions = [
            (0, -70),  # Haut
            (0, 70),   # Bas
            (-70, 0),  # Gauche
            (70, 0)    # Droite
        ]
        
        for dx, dy in directions:
            for i in range(1, self.range + 1):
                case_x = self.x + (dx * i)
                case_y = self.y + (dy * i)
                rect_case = pygame.Rect(case_x, case_y, 70, 70)
                bloque = False  
                for ligne in grille:
                    for tile in ligne:
                        if pygame.Rect.colliderect(rect_case, tile.rect):
                            if tile.tile_type == "mur":
                                bloque = True
                                break
                            
                            elif tile.tile_type == "mur_cassable":
                                self.zones_explosion.append(rect_case)
                                tile.break_wall() 
                                bloque = True
                                break
                            
                            elif tile.tile_type == "passage":
                                self.zones_explosion.append(rect_case)
                                break
                    if bloque:
                        break  
                        
                if bloque:
                    break

    def draw(self, screen, grille_du_jeu):
        if self.etat == "attente":
            pygame.draw.rect(screen, "black", self.rect)
        
        elif self.etat == "explosion":
            for zone in self.zones_explosion:
                pygame.draw.rect(screen, "red", zone)

        return grille_du_jeu
