from pettingzoo.test import parallel_api_test
from bombermanenv import BomberEnv

env = BomberEnv()

parallel_api_test(env, num_cycles=100)

env.close()