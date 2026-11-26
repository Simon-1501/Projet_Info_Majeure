# Structures de données et Algorithmes (`ALGORITHMS.md`)

## 1. 

## 2. Algorithmes de recherche de chemin (`Recherche.py`)


## 3. Arbre de décision du Boss (`Ai.py`)
Le comportement du Boss repose sur un **arbre de décision** hiérarchisant les priorités à chaque image :

```text
               [Le Boss est-il dans une zone de danger ?]
                          /                  \
                        OUI                  NON
                        /                      \
           [Fuir (algo en largeur)]          [Le joueur est-il à portée ?]
                                        /                  \
                                      OUI                  NON
                                      /                      \
                            [Poser une bombe]      [Poursuivre via Dijkstra]
```

* **Pourquoi cette structure ?** : L'arbre de décision garantit que la **survie** (esquiver ses propres bombes ou celles du joueur) reste toujours prioritaire sur l'**attaque** et la **poursuite**, rendant l'IA cohérente et réactive sans comportement suicidaire.
