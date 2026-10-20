import pygame

class Tile:
    def __init__(self, x, y, tile_type):
        self.tile_type = tile_type
        self.rect = pygame.Rect(x * 32, y * 32, 32, 32)

    def draw(self, screen):
        if self.tile_type == "mur":
            pygame.draw.rect(screen, (50, 50, 50), self.rect)
        elif self.tile_type == "mur_cassable":
            pygame.draw.rect(screen, (139, 69, 19), self.rect)  
        elif self.tile_type == "passage":
            pygame.draw.rect(screen, (34, 139, 34), self.rect)
