from labyrinthe import *
from tile import *
from statemachine import StateChart, State
import heapq


"""Legende : '#' = mur incassable, '+' = mur cassable, ' ' = chemin """

carte = ["###############",
         "#  +++++++++  #",
         "# #+#+#+#+#+# #",
         "# ++++++++++++#",
         "# #+#+#+#+#+#+#",
         "# ++++++++++++#",
         "# #+#+#+#+#+# #",
         "#             #",
         "###############"]

#print(graphe_carte)

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

def dijkstra(grille,s):
    gr = [[0]*len(grille[0])]*len(grille)
    for c in range(len(grille[0])):
        for l in range(len(grille)):
            if grille[l][c].current_state == "mur":
                gr[l][c] = "#"
            elif grille[l][c].current_state == "mur_cassable":
                gr[l][c] = "+"
            elif grille[l][c].current_state == "passage":
                gr[l][c] = " "
    print(gr)
    lab = Labyrinthe(gr)
    g = graphe_du_labyrinthe(lab)
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

#print(dijkstra(graphe_carte, (1,1))[1])

def reconstruire_chemin(s,t,p):
    if s not in p or t == s:
        return []
    c = [t]
    while t!=s:
        t = p[t]
        c.append(t)
    c.reverse()
    return c

def parcours_largeur(graphe, depart):
    """
    Visite les sommets atteignables depuis depart, les plus proches d'abord

    Returns:
        predecesseur : {sommet: sommet d'où l'on est arrivé}, None pour le départ.
        Ses clés sont les sommets déjà visités ou en attente dans la file.
    """
    a_visiter = [(depart.x,depart.y)]            # la file : premier arrivé, premier servi
    predecesseur = {(depart.x,depart.y): None}

    while a_visiter:
        sommet = a_visiter.pop()   # on retire le premier de la file
        for voisin in graphe[sommet]:
            if voisin not in predecesseur:
                predecesseur[voisin] = sommet
                a_visiter.append(voisin)
            pass

    return predecesseur

def trouver_joueur(pos_j,pos_AI,grille):
    p = parcours_largeur(grille,pos_AI)
    c = reconstruire_chemin(pos_AI,pos_j,p)
    return c