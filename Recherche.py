from labyrinthe import *

"""Legende : '#' = mur incassable, '+' = mur cassable, ' ' = chemin """

carte = ["###############",
         "#             #",
         "# + + + + + + #",
         "#             #",
         "# + + + + + + #",
         "#             #",
         "# + + + + + + #",
         "#             #",
         "###############"]

carte = Labyrinthe(carte)
graphe_carte = graphe_du_labyrinthe(carte)


"""Arcs valués"""
for i in graphe_carte:
    for j in range(len(graphe_carte[i])):
        T = graphe_carte[i][j]
        graphe_carte[i][j] = ((T[0],T[1]),1)
#print(graphe_carte)

def arc_sortant_min(g,M,d):
    d_min = float('inf')
    for x in M:
        for y,l in g[x]:
            if y not in M:
                if d[x] + l < d_min:
                    d_min=d[x]+l
                    x_min = x
                    y_min = y
    if d_min < float('inf'):
        return x_min,y_min,d_min
    return None

def dijkstra(g,s):
    M = [s]
    d = {s:0}
    p = {}
    while arc_sortant_min(g,M,d):
        x,y,l = arc_sortant_min(g,M,d)    
        M.append(y)
        p[y] = x
        d[y] = d[x] + l
    return(M,d,p)

#print(dijkstra(graphe_carte, (1,1)))

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