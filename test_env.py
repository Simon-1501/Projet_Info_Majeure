import numpy as np

from bombermanenv import BomberEnv


env = BomberEnv()

observations, infos = env.reset(seed=42)

print("Agents :", env.agents)

for agent, observation in observations.items():
    print(
        agent,
        "observation :",
        observation.shape,
        observation.dtype,
    )

for tour in range(20):
    if not env.agents:
        print("La partie est terminée.")
        break

    actions = {
        agent: env.action_space(agent).sample()
        for agent in env.agents
    }

    observations, rewards, terminations, truncations, infos = (
        env.step(actions)
    )

    print(f"Tour {tour + 1}")
    print("Actions :", actions)
    print("Récompenses :", rewards)
    print("Agents restants :", env.agents)

env.close()