class Labyrinthe:
    """Un labyrinthe décrit par une grille de caractères"""

    def __init__(self, grille):
        self.grille = grille
        self.depart = self.trouver("S")
        self.arrivee = self.trouver("E")

    def trouver(self, caractere):
        """Renvoie la position (ligne, colonne) d'un caractère de la grille"""
        for ligne in range(len(self.grille)):
            for colonne in range(len(self.grille[ligne])):
                if self.grille[ligne][colonne] == caractere:
                    return (ligne, colonne)

    def est_libre(self, position):
        """Vrai si la case existe et n'est pas un mur"""
        ligne, colonne = position
        if ligne < 0 or ligne >= len(self.grille):
            return False
        if colonne < 0 or colonne >= len(self.grille[ligne]):
            return False
        return self.grille[ligne][colonne] != "#" or self.grille[ligne][colonne] != "+"

    def voisines(self, position):
        """Renvoie les cases libres autour d'une position : haut, bas, gauche, droite"""
        ligne, colonne = position
        autour = [(ligne - 1, colonne), (ligne + 1, colonne), (ligne, colonne - 1), (ligne, colonne + 1)]
        cases = []
        for case in autour:
            if self.est_libre(case):
                cases.append(case)
        return cases

    def afficher(self, chemin=[]):
        """Affiche le labyrinthe, avec un point sur chaque case du chemin"""
        for ligne in range(len(self.grille)):
            texte = ""
            for colonne in range(len(self.grille[ligne])):
                if (ligne, colonne) in chemin and self.grille[ligne][colonne] == " ":
                    texte += "."
                else:
                    texte += self.grille[ligne][colonne]
            print(texte)

def graphe_du_labyrinthe(labyrinthe):
    """Renvoie le graphe des cases libres : {case: liste des cases voisines libres}"""
    graphe = {}

    for ligne in range(len(labyrinthe.grille)):
        for colonne in range(len(labyrinthe.grille[ligne])):
            case = (ligne, colonne)
            if labyrinthe.est_libre(case):
                graphe[case] = labyrinthe.voisines(case)

    return graphe