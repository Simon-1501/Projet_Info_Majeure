import pygame

class Bouton:
    def __init__(self, posx, posy, taillex, tailley, sprite, clic_state):
        self.pos = pygame.Vector2(posx,posy)
        self.sprite = pygame.transform.scale(sprite, (taillex, tailley)) 
        self.rect = self.sprite.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
        self.clic_state = clic_state

    def draw(self, screen):
        screen.blit(self.sprite, self.rect)