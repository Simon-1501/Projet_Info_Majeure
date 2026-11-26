'''On veut un graphe valué à partir de notre grille de jeu'''
import heapq
from tile import Tile


def creer_graph_boss(grille):
    """Renvoie le graphe valué des cases libres : {(ligne, col): [((voisin_lig, voisin_col), 1), ...]}"""
    graphe = {}
    nb_lignes = len(grille)
    nb_colonnes = len(grille)

    for ligne in range(nb_lignes):
        for colonne in range(nb_colonnes):
            case = (ligne, colonne)
            voisins = []

            for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nl = ligne + dl
                nc = colonne + dc

                # On vérifie que le voisin est bien dans les limites de la grille
                if 0 <= nl < nb_lignes and 0 <= nc < nb_colonnes:
                    if grille[nl][nc].current_state.value in ["fire", "passage"]:
                        voisins.append(((nl, nc), 1))

            graphe[case] = voisins

    return graphe


'''
for i in graphe_carte:
    for j in range(len(graphe_carte[i])):
        T = graphe_carte[i][j]
        graphe_carte[i][j] = ((T[1],T[0]),1)
#print(graphe_carte)


def dijkstra_hpq(g, s):
    d = {}
    d[s] = 0
    M = [(0, s)]
    p = {}
    while M:
        dist_x, x = heapq.heappop(M)
        if x not in d:
            d[x] = dist_x
        if dist_x <= d[x]:
            for y, l in g.get(x, []):
                nouvelle_dist = dist_x + l
                if y not in d or nouvelle_dist < d[y]:
                    d[y] = nouvelle_dist
                    p[y] = x
                    heapq.heappush(M, (nouvelle_dist, y))
    return d,p'''