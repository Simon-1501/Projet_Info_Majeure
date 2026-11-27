'''On veut un graphe valué à partir de notre grille de jeu'''
from tile import Tile


def creer_graph_boss(grille):
    """Renvoie le graphe valué des cases libres : {(ligne, col): [((voisin_lig, voisin_col), 1), ...]}"""
    graphe = {}
    nb_lignes = len(grille)
    nb_colonnes = len(grille[0])

    for ligne in range(nb_lignes):
        for colonne in range(nb_colonnes):
            case = (colonne, ligne)
            voisins = []

            for dc, dl in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nl = ligne + dl
                nc = colonne + dc

                # On vérifie que le voisin est bien dans les limites de la grille
                if 0 <= nl < nb_lignes and 0 <= nc < nb_colonnes:
                    if grille[nl][nc].current_state.value in ["fire", "passage"]:
                        voisins.append(((nc, nl), 1))

            graphe[case] = voisins
    return graphe

def arc_sortant_min(g, M, d):
    dmin = None
    xmin = None
    ymin = None
    for x in M:
        for (y,l) in g[x]:
            if y not in M:
                if dmin == None or d[x] + l < dmin:
                    dmin = d[x]+l
                    xmin = x
                    ymin = y
    if dmin == None:
        return None
    return (xmin, ymin, dmin)



def dijkstra(g,s):
    M = [s]
    p = {}
    d = {s:0}
    arc_choisi = arc_sortant_min(g,M,d)
    while arc_choisi != None:
        x,y,dmin = arc_choisi
        M.append(y)
        d[y] = dmin
        p[y] = x
        arc_choisi = arc_sortant_min(g,M,d)
    return (M,p,d)

def recherche_largeur(depart_l, graphe_carte, cases_dangereuses): #BFS
    depart = (int(depart_l[0]), int(depart_l[1]))  # (ligne, col)
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
    return case_sure, parents


def reconstruire_chemin(s,t,p):
    if s not in p.values() or t == s:
        return []
    c = [t]
    while t!=s:
        t = p[t]
        c.append(t)
    c.reverse()
    return c