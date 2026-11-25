# Bomberman - Projet Pygame & Intelligence Artificielle

Implémentation du jeu classique **Bomberman** développée en Python avec la bibliothèque **Pygame**, intégrant une modélisation par graphes, des arbres de décision et des algorithmes de recherche heuristique pour le comportement des ennemis.

---

## 1. Prérequis et Installation

### Prérequis
* **Python** : version 3.10 ou supérieure recommandée.
* **Pygame** : bibliothèque graphique 2D.

### Installation
1. Cloner le dépôt :
   ```bash
   git clone <https://github.com/Simon-1501/Projet_Info_Majeure>
   cd bomberman-pygame
   ```

2. Créer un environnement virtuel (recommandé) et installer les dépendances :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sous Linux/Mac
   # venv\Scripts\activate   # Sous Windows

   pip install -r requirements.txt
   ```

3. Lancer le jeu :
   ```bash
   python main.py
   ```

---

## 2. Commandes et Fonctionnalités

### Contrôles du joueur

| Touche | Action |
| :--- | :--- |
| **Flèches directionnelles** ou **Z, Q, S, D** | Déplacer le personnage |
| **Espace** ou **R_Shift** (majuscule droite)| Poser une bombe |
| **Échap** | Mettre le jeu en pause |

### Bonus disponibles
* 🔥 **Flamme +1** : Augmente la portée de l'explosion d'une case.
* 💣 **Bombe +1** : Permet de poser une bombe supplémentaire simultanément.
* ⚡ **Vitesse +1** : Augmente la vitesse de déplacement.

---

## 🗂️ 3. Architecture du Projet

Le code est structuré de cette façon :

```text
bomberman-pygame/
│
├── main.py              # Point d'entrée et boucle principale du jeu (60 FPS)
├── config.py            # Constantes globales (dimensions, couleurs, paramètres IA)
├── requirements.txt     # Dépendances Python
├── README.md            # Documentation du projet
│
├── assets/              # Sprites, polices et effets sonores
│
└── src/
    ├── jeu.py           # Gestion des états (Menu, En cours, Game Over) et collisions
    ├── carte.py         # Génération de la grille et gestion des murs/bonus
    ├── entites.py       # Classes Joueur, Ennemi et Bombe
    ├── graphe.py        # Modélisation de la carte sous forme de graphe dynamique
    └── ia.py            # Arbre de décision, algorithmes A* et BFS
```

---

### B. Arbre de Décision de l'IA (`src/ia.py`)
À chaque prise de décision, l'ennemi parcourt un **arbre binaire de décision** hiérarchisant sa survie avant l'attaque :

```text
                  [Est dans une zone de danger ?]
                        /               \
                      OUI               NON
                      /                   \
          [Fuir via BFS]         [Joueur à portée de bombe ?]
                                      /               \
                                    OUI               NON
                                    /                   \
                          [Poser une bombe]    [Poursuivre via A*]
```

### C. Algorithmes de Recherche
1. **BFS (Parcours en largeur) — Fuite et Zones de danger** :
   * Utilisé pour calculer la propagation des flammes d'une bombe et marquer les cases dangereuses.
   * Lorsqu'une IA est menacée, le BFS explore les cases voisines par couches successives afin de garantir le **chemin le plus court en nombre de cases vers la première zone sûre**.
   * *Complexité temporelle* : $O(|S| + |A|)$.

2. **Algorithme A\* (A-Star) — Poursuite du joueur** :
   * Permet à l'IA de contourner les murs pour traquer le joueur efficacement.
   * **Fonction de coût** : $f(n) = g(n) + h(n)$, où $g(n)$ est le coût réel depuis le départ et $h(n)$ l'heuristique.
   * **Heuristique choisie** : La **distance de Manhattan** $h(n) = |x_n - x_{cible}| + |y_n - y_{cible}|$. Les déplacements diagonaux étant interdits dans Bomberman, cette heuristique est **admissible** (elle ne surestime jamais le coût réel) et garantit un chemin optimal.
