import os
import pygame
import ray
import torch

from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.core.columns import Columns
from ray.rllib.core.rl_module.default_model_config import DefaultModelConfig
from ray.rllib.core.rl_module.multi_rl_module import MultiRLModuleSpec
from ray.rllib.core.rl_module.rl_module import RLModuleSpec
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.tune.registry import register_env

from bombermanenv import BomberEnv


# --------------------------------------------------
# CONFIGURATION DU MODELE
# --------------------------------------------------

def creer_environnement(config):
    return ParallelPettingZooEnv(BomberEnv(**config))


register_env("bomberman", creer_environnement)

cnn_config = DefaultModelConfig(
    conv_filters=[
        [16, 3, 1],
        [32, 3, 1],
    ],
    conv_activation="relu",
    head_fcnet_hiddens=[128],
)

config = (
    PPOConfig()
    .environment(
        env="bomberman",
        env_config={
            "render_mode": None,
            "max_cycles": 300,
        },
    )
    .env_runners(num_env_runners=0)
    .learners(num_learners=0, num_gpus_per_learner=0)
    .multi_agent(
        policies={"shared_policy"},
        policy_mapping_fn=lambda agent_id, *args, **kwargs: "shared_policy",
    )
    .rl_module(
        rl_module_spec=MultiRLModuleSpec(
            rl_module_specs={
                "shared_policy": RLModuleSpec(
                    model_config=cnn_config,
                ),
            },
        ),
    )
)


# --------------------------------------------------
# CHARGEMENT DU MODELE
# --------------------------------------------------

ray.init(ignore_reinit_error=True)

algo = None
env = None

try:
    
    #var
    tile_x = 70
    tile_y = 70
    screen_size_x = 1050
    screen_size_y = 630


    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((screen_size_x, screen_size_y))
    clock = pygame.time.Clock()
    running = True
    dt = 0




    algo = config.build()

    checkpoint_path = os.path.abspath("models/bomberman_ppo")
    algo.restore(checkpoint_path)

    # Récupération du module partagé par les deux IA.
    module = algo.get_module("shared_policy")

    print("Modèle PPO chargé !")

    # --------------------------------------------------
    # CREATION DE L'ENVIRONNEMENT DU MATCH
    # --------------------------------------------------

    env = BomberEnv(
        render_mode="human",
        max_cycles=300,
        num_players=2,
    )

    observations, infos = env.reset()

    clock = pygame.time.Clock()
    running = True

    # --------------------------------------------------
    # BOUCLE PRINCIPALE
    # --------------------------------------------------

    while running and not env.closed:

        # Limite approximative à 10 tours par seconde.
        # L'environnement avance de 0.1 seconde par tour.
        clock.tick(10)

        # La fenêtre Pygame est fermée ?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not running:
            break

        # Si une partie vient de se terminer, on en démarre une autre.
        if not env.agents:
            observations, infos = env.reset()

        actions = {}

        # Chaque IA choisit une action à partir de sa propre observation.
        for agent_id in env.agents:

            observation = observations[agent_id]

            # Conversion en tenseur et ajout de la dimension de lot.
            observation_tensor = torch.as_tensor(
                observation,
                dtype=torch.float32,
            ).unsqueeze(0)

            # Prédiction du modèle partagé.
            with torch.no_grad():
                sorties = module.forward_inference({
                    Columns.OBS: observation_tensor,
                })

                distribution_classe = (
                    module.get_inference_action_dist_cls()
                )

                distribution = distribution_classe.from_logits(
                    sorties[Columns.ACTION_DIST_INPUTS]
                )

                action_tensor = (
                    distribution.to_deterministic().sample()
                )

            # Conversion en entier Python.
            action = int(action_tensor.reshape(-1)[0].item())

            actions[agent_id] = action

        # Application simultanée des actions dans l'environnement.
        observations, rewards, terminations, truncations, infos = (
            env.step(actions)
        )

finally:
    # Fermeture propre des ressources.
    if env is not None:
        env.close()

    if algo is not None:
        algo.stop()

    ray.shutdown()
    pygame.quit()