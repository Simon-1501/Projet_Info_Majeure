from labyrinthe import *

carte = ["###############",
         "#             #",
         "# # # # # # # #",
         "#             #",
         "# # # # # # # #",
         "#             #",
         "# # # # # # # #",
         "#             #",
         "###############"]

carte = Labyrinthe(carte)
graphe_carte = graphe_du_labyrinthe(carte)

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

