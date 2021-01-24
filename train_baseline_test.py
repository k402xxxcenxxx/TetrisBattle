
import os
import gym

from stable_baselines.common.policies import MlpPolicy
from stable_baselines import PPO2
from stable_baselines.common import make_vec_env

from TetrisBattle.envs.tetris_env import TetrisSingleEnv

# load env var
def get_var_from_env(name, default=""):
    return os.getenv(name) if os.getenv(name) != None else default

CASE_NAME = get_var_from_env("CASE_NAME", "ppo2_tetris_test")
TRAIN_STEPS = int(float(get_var_from_env("TRAIN_STEPS", "1e5")))
TEST_STEPS = int(float(get_var_from_env("TEST_STEPS", "1e3")))
VERBOSE = int(get_var_from_env("VERBOSE", "1"))
TENSORBOARD_LOG_PATH = get_var_from_env("TENSORBOARD_LOG_PATH", "./tensorboard/ppo2_tetris_test")
GRIDCHOICE = get_var_from_env("GRIDCHOICE", "none")

os.makedirs(TENSORBOARD_LOG_PATH, exist_ok=True)

env = make_vec_env(TetrisSingleEnv, n_envs=1, env_kwargs={"gridchoice": GRIDCHOICE, "obs_type": "grid", "mode": "rgb_array"})

# Train the agent
model = PPO2(MlpPolicy, env, verbose=1, nminibatches=4, tensorboard_log=TENSORBOARD_LOG_PATH)

model.learn(total_timesteps=TRAIN_STEPS)
model.save(CASE_NAME)

del model # remove to demonstrate saving and loading

# Test
env = TetrisSingleEnv(gridchoice=GRIDCHOICE, obs_type="grid", mode="rgb_array")
model = PPO2.load(CASE_NAME)
obs = env.reset()

t = 0
while t < TEST_STEPS:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()
    t += 1

print("SUCCESS")