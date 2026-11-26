import pygame
from tile import Tile
from Recherche_Boss import *
import os

class Boss:
    """ On définit cette classe comme un joueur, mais un peu modifié. On a comme méthodes"""
    def __init__(self, nom, vie_max, x, y, object=None):
        self.object = object
        self.nom = nom
        self.vie_max = vie_max
        self.vie = vie_max

        self.degats_recus_ce_tour = 0

        self.sprite = pygame.image.load(os.path.join('Sprites', 'AI.png')).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (70, 70)) 
            

        self.pos_grille = [x, y]
        self.pos = pygame.Vector2(x*70, y*70)



        self.move_timer = 0
        self.MOVE_COOLDOWN = 0.5
        self.damage_timer = 0
        self.bomb_timer = 0
        self.BOMB_COOLDOWN = 3.0    # Temps d'attente entre deux poses de bombe
        self.portee_bombe = 2       # Distance en cases pour poser une bombe

    def est_vivant(self):
        return self.vie > 0

    def take_damages(self, damages):
        vie_avant = self.vie
        self.vie = max(0, self.vie - damages)
        degats_reels = vie_avant - self.vie
        self.degats_recus_ce_tour += degats_reels

    def update(self, grille, dt):
        self.degats_recus_ce_tour = 0

        if not self.est_vivant():
            return

        if self.damage_timer > 0:
            self.damage_timer -= dt

        if self.bomb_timer > 0:
            self.bomb_timer -= dt

        x = int(self.pos_grille[0])
        y = int(self.pos_grille[1])

        case_actuelle = grille[y][x]

        if case_actuelle.current_state == Tile.fire:
            if self.damage_timer <= 0:
                self.take_damages(1)
                self.damage_timer = 2


    """On a maintenant les méthodes spécifiques"""
    # Vérifier s'il y a une bombe
    def est_en_danger(self, cases_dangereuses):
        pos_actuelle = (int(self.pos_grille[1]), int(self.pos_grille[0]))  # (ligne, col)
        return pos_actuelle in cases_dangereuses

    def fuir(self, dt, grille, graphe_carte, cases_dangereuses):
        if self.move_timer > 0:
            self.move_timer -= dt
            return False

        depart = (int(self.pos_grille[1]), int(self.pos_grille[0]))  # (ligne, col)
        file = [depart]
        parents = {depart: None}
        case_sure = None

        while len(file) > 0:
            case = file.pop(0)
            if case not in cases_dangereuses:
                case_sure = case
                break

            for voisin, dist in graphe_carte[case]: #on a une distance de 1, cherchez pas
                if voisin not in parents:
                    parents[voisin] = case
                    file.append(voisin)

        """On regarde les voisins de la case de départ, et on enchaine jusqu'à tomber sur une case sure (ou avoir exploré tous les voisins)"""
        if case_sure is not None and case_sure != depart:
            chemin = reconstruire_chemin(depart, case_sure, parents)
            if len(chemin) > 0:
                self._deplacer_vers_case(chemin[0], grille)

    #Vérifier si le joueur est assez proche
    def joueur_a_portee(self, pos_joueur):
        """
        Vérifie si le joueur est à portée d'attaque (en ligne droite ou distance Manhattan)
        et si le boss peut poser une bombe.
        """

        if self.bomb_timer > 0:
            return False

        x_boss, y_boss = int(self.pos_grille[0]), int(self.pos_grille[1])
        x_joueur, y_joueur = int(pos_joueur[0]), int(pos_joueur[1])

        distance = abs(x_boss - x_joueur) + abs(y_boss - y_joueur)
        return distance <= self.portee_bombe

    def peut_poser_bombe(self):
        """Réinitialise le timer quand le boss pose une bombe dans le main."""
        self.bomb_timer = self.BOMB_COOLDOWN

    # --- MÉTHODE 3 : Se rapprocher du joueur ---
    def se_rapprocher(self, dt, pos_joueur, grille, graphe_carte, cases_dangereuses=None):
        """Avance d'une case vers le joueur grâce à Dijkstra."""
        if self.move_timer > 0:
            self.move_timer -= dt
            if self.move_timer > 0:
                return None
            else:
                self.move_timer = 0

        depart = (int(self.pos_grille[1]), int(self.pos_grille[0]))      # (ligne, col)
        arrive = (int(pos_joueur[1]), int(pos_joueur[0]))                # (ligne, col)

        M, p, d = dijkstra(graphe_carte, depart)
        chemin = reconstruire_chemin(depart, arrive, p)

        if len(chemin) == 0:
        # S'il est bloqué par des murs cassables et que son timer est prêt, il pose une bombe !
            if self.bomb_timer <= 0:
                return "poser_bombe"
            return None

        
        prochaine_case = chemin[0]
        print(prochaine_case)
        # On évite de marcher volontairement dans une explosion si on n'y est pas déjà
        if cases_dangereuses is not None and prochaine_case in cases_dangereuses:
            return None

        self._deplacer_vers_case(prochaine_case, grille)


    # Methode interne de déplacement du boss, C'est pour faire le déplacement sur un tour (en combiner plusieurs permet un déplacement complet)
    def _deplacer_vers_case(self, prochaine_case, grille):
        x_grid = int(self.pos_grille[0])
        y_grid = int(self.pos_grille[1])

        nb_lignes = len(grille)
        nb_colonnes = len(grille[0])

        deplacement_effectue = False
        
        if prochaine_case[0] > y_grid:
            if y_grid < nb_lignes - 1 and grille[y_grid + 1][x_grid].current_state.value in ["fire", "passage"]:
                self.pos_grille[1]+=1
                deplacement_effectue = True
        elif prochaine_case[0] < y_grid:
            if y_grid > 0 and grille[y_grid - 1][x_grid].current_state.value in ["fire", "passage"]:
                self.pos_grille[1]-=1
                deplacement_effectue = True
        elif prochaine_case[1] < x_grid:
            if x_grid > 0 and grille[y_grid][x_grid - 1].current_state.value in ["fire", "passage"]:
                self.pos_grille[0]-=1
                deplacement_effectue = True
        elif prochaine_case[1] > x_grid:
            if x_grid < nb_colonnes - 1 and grille[y_grid][x_grid + 1].current_state.value in ["fire", "passage"]:
                self.pos_grille[0]+=1
                deplacement_effectue = True

        if deplacement_effectue:
            self.move_timer = self.MOVE_COOLDOWN
            self.pos =  pygame.Vector2(self.pos_grille[0]*70, self.pos_grille[1]*70)
    def show(self, screen):
        rect_boss = self.sprite.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
        screen.blit(self.sprite, rect_boss)
