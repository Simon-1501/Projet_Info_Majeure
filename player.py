import pygame

class Player:
    def __init__(self,  nom, vie_max, x, y, object=None):
        self.object = object
        self.nom = nom
        self.vie_max = vie_max
        self.vie = vie_max
        self.speed = 150
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 40, 50)


    def est_vivant(self):
        if self.vie > 0:
            return True

    def take_damages(self, damages):
        self.vie -= damages
        if self.vie <= 0:
            self.vie = 0

    def take_object(self, object):
        self.object = object

    def move(self, dt, keys, grille):
        mouvement = pygame.Vector2(0, 0)

        if keys[pygame.K_z]:
                mouvement.y -= self.speed * dt
        elif keys[pygame.K_s]:
                mouvement.y += self.speed * dt
        elif keys[pygame.K_q]:
                mouvement.x -= self.speed * dt
        elif keys[pygame.K_d]:
                mouvement.x += self.speed * dt

        
         # déplacement et collision sur l'axe X
        self.pos.x += mouvement.x
        self.rect.x = int(self.pos.x) # met à jour le rectangle de collision

        for ligne in grille:
            for tile in ligne:
                if tile.tile_type != "passage": # Si c'un mur ou un mur cassable
                    if self.rect.colliderect(tile.rect):
                        if mouvement.x > 0:
                            self.rect.right = tile.rect.left
                        if mouvement.x < 0:
                            self.rect.left = tile.rect.right
                        self.pos.x = self.rect.x

        # déplacement et collision sur l'axe Y
        self.pos.y += mouvement.y
        self.rect.y = int(self.pos.y)
    
        for ligne in grille:
            for tile in ligne:
                if tile.tile_type != "passage":
                    if self.rect.colliderect(tile.rect):
                        # Si on allait en bas
                        if mouvement.y > 0:
                            self.rect.bottom = tile.rect.top
                        # Si on allait en haut
                        if mouvement.y < 0:
                            self.rect.top = tile.rect.bottom
                        self.pos.y = self.rect.y


    def show(self, sprite, screen):
        # affichage aux bonnes coordonnées
        rect_joueur = sprite.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
        screen.blit(sprite, rect_joueur)
