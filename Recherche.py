from labyrinthe import *
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

carte = Labyrinthe(carte)
graphe_carte = graphe_du_labyrinthe(carte)
print(graphe_carte)

"""Arcs valués"""
for i in graphe_carte:
    for j in range(len(graphe_carte[i])):
        T = graphe_carte[i][j]
        graphe_carte[i][j] = ((T[1],T[0]),1)
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
    return d,p

def dijkstra(g,s):
    #s = [s.x,s.y]
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