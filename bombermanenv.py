import os

import gymnasium
import numpy as np
import pygame

from pettingzoo import ParallelEnv

from player import Player
from tile import Tile


class BomberEnv(ParallelEnv):
    """
    Environnement Bomberman multi-agent grâce à PettingZoo.

    Actions :
        0 : Haut
        1 : Bas
        2 : Gauche
        3 : Droite
        4 : Ne rien faire
        5 : Poser une bombe

    Les quatre joueurs partagent la même grille.
    """

    metadata = {
        "name": "bomberman",
        "render_modes": ["human"],
        "is_parallelizable": True,
    }

    def __init__(self, render_mode=None, max_cycles=2000):
        super().__init__()

        self.render_mode = render_mode
        self.max_cycles = max_cycles

        # Dimensions de la carte
        self.tile_x = 70
        self.tile_y = 70

        self.screen_size_x = 1050
        self.screen_size_y = 630

        self.nb_lignes = 9
        self.nb_colonnes = 15

        # Agents
        self.possible_agents = [
            "joueur_1",
            "joueur_2",
            "joueur_3",
            "joueur_4",
        ]

        self.agents = []

        # Une politique peut choisir parmi six actions.
        self._action_spaces = {
            agent: gymnasium.spaces.Discrete(6)
            for agent in self.possible_agents
        }

        # 6 canaux de 9 x 15 :
        # canal 0 : terrain
        # canaux 1 à 4 : positions des joueurs
        # canal 5 : position du joueur observateur
        self._observation_spaces = {
            agent: gymnasium.spaces.Box(
                low=0,
                high=255,
                shape=(6, self.nb_lignes, self.nb_colonnes),
                dtype=np.uint8,
            )
            for agent in self.possible_agents
        }

        self.screen = None
        self.clock = None
        self.sprites = None

        self.grille_du_jeu = []
        self.players = []

        self.cycles = 0
        self.closed = False

    def action_space(self, agent):
        return self._action_spaces[agent]

    def observation_space(self, agent):
        return self._observation_spaces[agent]

    # --------------------------------------------------
    # INITIALISATION
    # --------------------------------------------------

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.np_random = np.random.default_rng(seed)

        self.agents = self.possible_agents[:]
        self.cycles = 0
        self.closed = False

        # Carte originale
        self.map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1],
            [1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1],
            [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        # Création de la grille
        self.grille_du_jeu = []

        for y, ligne in enumerate(self.map):
            ligne_de_tiles = []

            for x, valeur in enumerate(ligne):
                tile = Tile(
                    x * self.tile_x,
                    y * self.tile_y,
                    x,
                    y,
                )

                if valeur == 1:
                    tile.build()

                elif valeur == 2:
                    tile.build_cassable()

                ligne_de_tiles.append(tile)

            self.grille_du_jeu.append(ligne_de_tiles)

        # Les sprites seront chargés uniquement si le jeu est affiché.
        # L'entraînement pourra donc fonctionner sans fenêtre Pygame.
        self.players = [
            Player(
                None, "Joueur 1", 3,
                self.tile_x, self.tile_y,
                None, None, None, None, None,
            ),
            Player(
                None, "Joueur 2", 3,
                self.tile_x * 13, self.tile_y,
                None, None, None, None, None,
            ),
            Player(
                None, "Joueur 3", 3,
                self.tile_x, self.tile_y * 7,
                None, None, None, None, None,
            ),
            Player(
                None, "Joueur 4", 3,
                self.tile_x * 13, self.tile_y * 7,
                None, None, None, None, None,
            ),
        ]

        # Vérifier que les positions de départ sont accessibles.
        for player in self.players:
            x = int(player.pos_grille[0])
            y = int(player.pos_grille[1])

            if self.grille_du_jeu[y][x].current_state != Tile.passage:
                raise RuntimeError(
                    f"Position de départ invalide : ({x}, {y})"
                )

        observations = {
            agent: self.observe(agent)
            for agent in self.agents
        }

        infos = {
            agent: {}
            for agent in self.agents
        }

        return observations, infos

    # --------------------------------------------------
    # OBSERVATIONS
    # --------------------------------------------------

    def observe(self, agent):
        """
        Retourne une observation numérique de forme (6, 9, 15).
        """

        observation = np.zeros(
            (6, self.nb_lignes, self.nb_colonnes),
            dtype=np.uint8,
        )# Création d'un tableau rempli de 0, en 3D ici (nbr de canaux, et grille donc canaux*longueur*largeur)
         # On remplie ensuite canal par canal
        # Canal 0 : état du terrain
        codes_terrain = {
            Tile.passage: 0,
            Tile.mur: 1,
            Tile.mur_cassable: 2,
            Tile.bomb: 3,
            Tile.fire: 4,
        }

        for y, ligne in enumerate(self.grille_du_jeu):
            for x, tile in enumerate(ligne):
                observation[0, y, x] = codes_terrain[
                    tile.current_state
                ]

        # Canaux 1 à 4 : position de chaque joueur.
        # Les joueurs morts ne sont plus représentés ici.
        for i, player in enumerate(self.players):
            if player.est_vivant():
                x = int(player.pos_grille[0])
                y = int(player.pos_grille[1])

                observation[i + 1, y, x] = 1

        # Canal 5 : position du joueur observateur.
        player_index = self.possible_agents.index(agent)
        player = self.players[player_index]

        if player.est_vivant():
            x = int(player.pos_grille[0])
            y = int(player.pos_grille[1])

            observation[5, y, x] = 1

        return observation

    # --------------------------------------------------
    # SIMULATION
    # --------------------------------------------------

    def step(self, actions):
        """
        actions est un dictionnaire :
        {
            "joueur_1": action_1,
            "joueur_2": action_2,
            ...
        }
        """

        if not self.agents:
            return {}, {}, {}, {}, {}

        agents_actifs = self.agents.copy()

        # Vérifier que chaque agent actif a fourni une action.
        if set(actions.keys()) != set(agents_actifs):
            raise ValueError(
                "Le dictionnaire actions doit contenir "
                "exactement les agents actifs."
            )

        for agent, action in actions.items():
            if not self.action_space(agent).contains(action):
                raise ValueError(
                    f"Action invalide pour {agent} : {action}"
                )

        self.cycles += 1

        # Pas de temps fixe : indépendant de la vitesse d'affichage.
        dt = 0.1

        # Conserver les vies avant la mise à jour.
        vies_avant = [
            player.vie
            for player in self.players
        ]

        # 1. Mise à jour des bombes et des explosions.
        for ligne in self.grille_du_jeu:
            for tile in ligne:
                tile.update(dt, self.grille_du_jeu)

        # 2. Mise à jour des joueurs.
        # Les actions sont définies pour tous les agents avant
        # de passer au prochain tour.
        for agent in agents_actifs:
            index = self.possible_agents.index(agent)
            player = self.players[index]

            if not player.est_vivant():
                continue

            player.update(self.grille_du_jeu, dt)

            action = int(actions[agent])

            # Actions 0 à 4 : déplacement ou immobilité.
            if action in (0, 1, 2, 3, 4):
                player.move_action(
                    action,
                    dt,
                    self.grille_du_jeu,
                )

            # Action 5 : poser une bombe.
            elif action == 5:
                x = int(player.pos_grille[0])
                y = int(player.pos_grille[1])

                tile = self.grille_du_jeu[y][x]

                if tile.current_state == Tile.passage:
                    tile.timer = 0
                    tile.drop()

        # 3. Calcul des récompenses.
        rewards = {
            agent: -0.01
            for agent in agents_actifs
        }

        terminations = {
            agent: False
            for agent in agents_actifs
        }

        truncations = {
            agent: False
            for agent in agents_actifs
        }

        for agent in agents_actifs:
            index = self.possible_agents.index(agent)
            player = self.players[index]

            perte_vies = vies_avant[index] - player.vie

            if perte_vies > 0:
                rewards[agent] -= 0.2 * perte_vies

            if not player.est_vivant():
                rewards[agent] -= 1.0
                terminations[agent] = True

        # 4. Déterminer les joueurs encore vivants.
        survivants = [
            agent
            for agent in self.possible_agents
            if self.players[
                self.possible_agents.index(agent)
            ].est_vivant()
        ]

        # Fin de partie si un seul joueur ou aucun joueur survit.
        fin_partie = len(survivants) <= 1

        # Fin de partie si la limite de tours est atteinte.
        limite_atteinte = self.cycles >= self.max_cycles

        if fin_partie:
            if len(survivants) == 1:
                gagnant = survivants[0]
                rewards[gagnant] += 1.0

            for agent in agents_actifs:
                terminations[agent] = True

            self.agents = []

        elif limite_atteinte:
            for agent in agents_actifs:
                truncations[agent] = True

            self.agents = []

        else:
            # Les joueurs éliminés quittent l'ensemble des agents actifs.
            self.agents = survivants

        # 5. Construire les observations des agents qui continuent.
        observations = {
            agent: self.observe(agent)
            for agent in self.agents
        }

        infos = {
            agent: {}
            for agent in agents_actifs
        }

        if self.render_mode == "human":
            self.render()

        return (
            observations,
            rewards,
            terminations,
            truncations,
            infos,
        )

    # --------------------------------------------------
    # AFFICHAGE
    # --------------------------------------------------

    def render(self):
        if self.closed:
            return

        if not pygame.get_init():
            pygame.init()

        if self.screen is None:
            self.screen = pygame.display.set_mode(
                (self.screen_size_x, self.screen_size_y)
            )

            pygame.display.set_caption("Bomberman - Multi-agent")

            self.clock = pygame.time.Clock()

        # Charger les sprites une seule fois.
        if self.sprites is None:
            dossier = os.path.dirname(os.path.abspath(__file__))

            sprite1 = pygame.image.load(
                os.path.join(dossier, "Sprites", "PLAYER1.png")
            ).convert_alpha()

            sprite2 = pygame.image.load(
                os.path.join(dossier, "Sprites", "PLAYER2.png")
            ).convert_alpha()

            self.sprites = [
                pygame.transform.scale(sprite1, (70, 70)),
                pygame.transform.scale(sprite2, (70, 70)),
            ]

            self.players[0].sprite = self.sprites[0]
            self.players[1].sprite = self.sprites[1]
            self.players[2].sprite = self.sprites[1]
            self.players[3].sprite = self.sprites[1]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return

        self.screen.fill("grey")

        for ligne in self.grille_du_jeu:
            for tile in ligne:
                tile.draw(self.screen)

        for player in self.players:
            if player.est_vivant():
                player.show(self.screen)

        pygame.display.flip()

    def close(self):
        self.closed = True

        if self.screen is not None:
            pygame.display.quit()
            self.screen = None

        self.clock = None