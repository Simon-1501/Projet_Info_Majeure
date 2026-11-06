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

    def __init__(self, render_mode=None, max_cycles=2000, num_players=4):
        super().__init__()

        if num_players not in (2, 3, 4):
            raise ValueError("num_players doit être 2, 3 ou 4.")

        self.num_players = num_players
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
        ][:self.num_players]

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
                low=0.0,
                high=4.0,
                shape=(self.nb_lignes, self.nb_colonnes, 6),
                dtype=np.float32,
            )
            for agent in self.possible_agents
        }

        self.screen = None
        self.clock = None
        self.sprites = None

        self.grille_du_jeu = []
        self.players = []

        self.bomb_owners = {}

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
        pygame.init()
        if seed is not None:
            self.np_random = np.random.default_rng(seed)


        self.bombes_actives = []  # {"x": 3, "y": 1, "timer": 10, "owner": "joueur_1"}


        self.bomb_owners = {}

        self.agents = self.possible_agents[:]
        self.cycles = 0
        self.closed = False

        # Carte originale
        self.map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1],
            [1, 2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1],
            [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1],
            [1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
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

        self.players = self.players[:self.num_players]


        # Vérifier que les positions de départ sont accessibles.
        for player in self.players:
            x = int(player.pos_grille[0])
            y = int(player.pos_grille[1])

            if self.grille_du_jeu[y][x].current_state != Tile.passage:
                raise RuntimeError(
                    f"Position de départ invalide : ({x}, {y})"
                )
        self.bomb_owners = {}
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
            (self.nb_lignes, self.nb_colonnes, 6),
            dtype=np.float32,
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
                observation[y, x, 0] = codes_terrain[
                    tile.current_state
                ]

        # Canaux 1 à 4 : position de chaque joueur.
        # Les joueurs morts ne sont plus représentés ici.
        for i, player in enumerate(self.players):
            if player.est_vivant():
                x = int(player.pos_grille[0])
                y = int(player.pos_grille[1])

                observation[y, x, i + 1] = 1

        # Canal 5 : position du joueur observateur.
        player_index = self.possible_agents.index(agent)
        player = self.players[player_index]

        if player.est_vivant():
            x = int(player.pos_grille[0])
            y = int(player.pos_grille[1])

            observation[y, x, 5] = 1

        return observation.copy()


    def _cases_explosion(self, x, y, etats_avant):
        """Retourne les cases touchées par une explosion de portée 3."""
        cases = {(x, y)}

        directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ]

        for dx, dy in directions:
            for distance in range(1, 4):
                nx = x + dx * distance
                ny = y + dy * distance

                if not (
                    0 <= nx < self.nb_colonnes
                    and 0 <= ny < self.nb_lignes
                ):
                    break

                etat = etats_avant[ny][nx]

                # Un mur indestructible bloque l'explosion.
                if etat == Tile.mur:
                    break

                # La case est touchée par l'explosion.
                cases.add((nx, ny))

                # Un mur cassable bloque les cases suivantes.
                if etat == Tile.mur_cassable:
                    break

        return cases
        
    # --------------------------------------------------
    # SIMULATION
    # --------------------------------------------------

    def step(self, actions):
        """Exécute un tour et calcule les récompenses des agents."""

        if not self.agents:
            return {}, {}, {}, {}, {}

        agents_actifs = self.agents.copy()

        # Vérifier les actions reçues.
        if set(actions.keys()) != set(agents_actifs):
            raise ValueError(
                "Le dictionnaire actions doit contenir exactement "
                "les agents actifs."
            )

        for agent, action in actions.items():
            if not self.action_space(agent).contains(action):
                raise ValueError(f"Action invalide pour {agent} : {action}")

        self.cycles += 1
        dt = 0.1

        # État des joueurs avant le tour.
        vies_avant = {}
        positions_avant = {}

        for agent in agents_actifs:
            player = self.players[self.possible_agents.index(agent)]

            vies_avant[agent] = player.vie
            positions_avant[agent] = (
                int(player.pos_grille[0]),
                int(player.pos_grille[1]),
            )

            # Réinitialiser le compteur, même si le joueur est déjà éliminé.
            player.degats_recus_ce_tour = 0

        # Mémoriser le terrain avant les explosions pour détecter
        # les murs cassables détruits pendant ce tour.
        etats_avant = [
            [tile.current_state for tile in ligne]
            for ligne in self.grille_du_jeu
        ]

        # Une entrée par propriétaire de bombe.
        # Chaque entrée contient les coordonnées touchées par son explosion.
        explosion_events = {}

        # --- CORRECTION DE LA RECOMPENSE DE BASE ---
        # Pénalité de temps très légère (-0.001) au lieu de -0.1 pour stopper la passivité
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

        # --------------------------------------------------
        # 1. Mise à jour des bombes et des explosions
        # --------------------------------------------------

        for ligne in self.grille_du_jeu:
            for tile in ligne:
                tile.update(
                    dt,
                    self.grille_du_jeu,
                    bomb_owners=self.bomb_owners,
                    explosion_events=explosion_events,
                )

        # --------------------------------------------------
        # 2. Récompenses pour les murs cassables détruits
        # --------------------------------------------------

        murs_recompenses = set()

        for proprietaire, cases in explosion_events.items():
            if proprietaire not in rewards:
                continue

            for x, y in cases:
                etat_avant = etats_avant[y][x]
                etat_apres = self.grille_du_jeu[y][x].current_state

                if (
                    etat_avant == Tile.mur_cassable
                    and etat_apres != Tile.mur_cassable
                    and (x, y) not in murs_recompenses
                ):
                    rewards[proprietaire] += 1
                    murs_recompenses.add((x, y))

        # --------------------------------------------------
        # 3. Mise à jour des joueurs et exécution des actions
        # --------------------------------------------------

        responsables_dommages = {
            agent: []
            for agent in agents_actifs
        }

        for agent in agents_actifs:
            index = self.possible_agents.index(agent)
            player = self.players[index]

            if not player.est_vivant():
                continue

            # Position à laquelle les dégâts éventuels seront reçus.
            x = int(player.pos_grille[0])
            y = int(player.pos_grille[1])

            # Mettre à jour le joueur avant son déplacement.
            player.update(self.grille_du_jeu, dt)

            # Identifier les propriétaires du feu responsable des dégâts.
            if player.degats_recus_ce_tour > 0:
                case = self.grille_du_jeu[y][x]

                proprietaires_feu = list(case.fire_owners)

                # Si plusieurs explosions se chevauchent, on privilégie
                # un adversaire à soi-même pour éviter de créditer
                # une auto-élimination à son propre propriétaire.
                proprietaires_adverses = [
                    p for p in proprietaires_feu
                    if p != agent and p in rewards
                ]

                if proprietaires_adverses:
                    proprietaires_adverses.sort(
                        key=lambda p: self.possible_agents.index(p)
                    )
                    responsable = proprietaires_adverses[0]

                elif agent in proprietaires_feu:
                    responsable = agent

                else:
                    responsable = None

                # Enregistrer un responsable par point de vie perdu.
                for _ in range(player.degats_recus_ce_tour):
                    responsables_dommages[agent].append(responsable)

            # Un joueur éliminé par les dégâts ne doit plus agir.
            if not player.est_vivant():
                continue

            action = int(actions[agent])

            if action in (0, 1, 2, 3, 4):
                player.move_action(
                    action,
                    dt,
                    self.grille_du_jeu,
                )

            elif action == 5:
                x = int(player.pos_grille[0])
                y = int(player.pos_grille[1])

                tile = self.grille_du_jeu[y][x]

                # Vérifier si le joueur possède déjà une bombe active.
                possede_bombe = any(
                    proprietaire == agent
                    for proprietaire in self.bomb_owners.values()
                )

                # Autoriser la pose uniquement si le joueur n'a pas de bombe active.
                if not possede_bombe and tile.current_state == Tile.passage:
                    tile.timer = 0
                    tile.drop()

                    if tile.current_state == Tile.bomb:
                        self.bomb_owners[(x, y)] = agent

                        # Récompense pour la pose d'une bombe.
                        rewards[agent] += 0.3

        # --------------------------------------------------
        # ADDITION : Récompense de survie à sa propre bombe
        # --------------------------------------------------
        # Si une bombe de l'agent a explosé ce tour-ci, on regarde s'il y a survécu
        for proprietaire, cases in explosion_events.items():
            if proprietaire in agents_actifs:
                p_index = self.possible_agents.index(proprietaire)
                p_player = self.players[p_index]
                
                # Si le joueur est toujours en vie après la phase de résolution des dégâts
                if p_player.est_vivant():
                    p_x = int(p_player.pos_grille[0])
                    p_y = int(p_player.pos_grille[1])
                    
                    # S'il n'est PAS sur une des cases touchées par sa bombe = FUITE REUSSIE !
                    if (p_x, p_y) not in cases:
                        rewards[proprietaire] += 1.5

        # --------------------------------------------------
        # 4. Récompenses pour les dégâts et les éliminations
        # --------------------------------------------------

        for agent in agents_actifs:
            index = self.possible_agents.index(agent)
            player = self.players[index]

            perte_vies = vies_avant[agent] - player.vie

            if perte_vies <= 0:
                continue

            responsables = responsables_dommages[agent]

            # Récompenser l'attaquant pour chaque dégât réellement infligé.
            for responsable in responsables:
                if responsable is not None and responsable != agent:
                    if responsable in rewards:
                        rewards[responsable] += 8

            # Déterminer si le joueur a été éliminé pendant ce tour.
            elimine = (
                vies_avant[agent] > 0
                and not player.est_vivant()
            )

            if elimine:
                # Pénalité de mort : -2 au total.
                rewards[agent] -= 10.0

                # Le dernier responsable adverse reçoit le bonus
                # d'élimination complémentaire.
                responsable_final = (
                    responsables[-1] if responsables else None
                )

                if (
                    responsable_final is not None
                    and responsable_final != agent
                    and responsable_final in rewards
                ):
                    # +0,8 pour le dégât final et +1,2 supplémentaire
                    # pour l'élimination : +2 au total pour l'attaquant.
                    rewards[responsable_final] += 20

            else:
                # Le joueur a perdu une ou plusieurs vies, mais survit.
                rewards[agent] -= 2.0 * perte_vies

        # --------------------------------------------------
        # 5. Déterminer les survivants et la fin de partie
        # --------------------------------------------------

        survivants = [
            agent
            for agent in agents_actifs
            if self.players[
                self.possible_agents.index(agent)
            ].est_vivant()
        ]

        fin_partie = len(survivants) <= 1
        limite_atteinte = self.cycles >= self.max_cycles

        if fin_partie:
            # Bonus de victoire s'il reste exactement un survivant.
            if len(survivants) == 1:
                gagnant = survivants[0]
                rewards[gagnant] += 10.0

            # Tous les agents encore actifs terminent leur épisode.
            for agent in agents_actifs:
                terminations[agent] = True

            self.agents = []

        elif limite_atteinte:
            # Tous les agents actifs sont tronqués à la limite.
            for agent in agents_actifs:
                truncations[agent] = True
            self.agents = []
        else:
        # La partie continue : les agents éliminés sont terminés.
            for agent in agents_actifs:
                player = self.players[
                    self.possible_agents.index(agent)
                    ]
                if not player.est_vivant():
                    terminations[agent] = True
            self.agents = survivants
        # --------------------------------------------------
        # 6. Observations et informations de sortie
        # --------------------------------------------------
        observations = {
                agent: self.observe(agent)
                 for agent in agents_actifs
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

        # Vérifier si la fenêtre existe toujours.
        surface_actuelle = pygame.display.get_surface()

        if (
            not pygame.display.get_init()
            or surface_actuelle is None
            or self.screen is None
        ):
            pygame.display.init()
            self.screen = pygame.display.set_mode(
                (self.screen_size_x, self.screen_size_y)
            )
            pygame.display.set_caption("Bomberman - Multi-agent")
            self.clock = pygame.time.Clock()
        else:
            self.screen = surface_actuelle

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

        # IMPORTANT : attribuer un sprite à chaque joueur avant player.show().
        for i, player in enumerate(self.players):
            if player.sprite is None:
                player.sprite = self.sprites[i % len(self.sprites)]

        # Gérer les événements de la fenêtre.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return

        # Dessiner le jeu
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