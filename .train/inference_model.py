from TetrisBattle.envs.tetris_env import TetrisSingleEnv

import gym

from stable_baselines.common.policies import MlpPolicy
from stable_baselines import PPO2
from stable_baselines.common import make_vec_env

import pickle
import numpy as np
import time
import os

# load env var
def get_var_from_env(name, default=""):
    return os.getenv(name) if os.getenv(name) != None else default

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0" #(or "1" or "2")

CASE_NAME = get_var_from_env("CASE_NAME", "ppo2_tetris_test")
GRIDCHOICE = get_var_from_env("GRIDCHOICE", "none")

np.set_printoptions(edgeitems=30, linewidth=20000, 
    formatter=dict(float=lambda x: "%3.1g" % x))

env = TetrisSingleEnv(gridchoice=GRIDCHOICE, obs_type="grid", mode="human")

model = PPO2.load(CASE_NAME)

action_meaning = {
    0: "NOOP",
    1: "hold",
    2: "drop",
    3: "rotate_right",
    4: "rotate_left",
    5: "right",
    6: "left",
    7: "down"
}

obs = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    
    # print(np.array(obs[0][360:]).reshape(-1, 18)[:20, :10])

    print(action_meaning[action])
    time.sleep(1/60 * 10)
    
    if dones:
        print("///")
        print("///")
        print("///")
        print("///")
        print("///")
        print("///")
        print("///")
        time.sleep(5)
        env.reset()
    else:
        print(np.array(obs).reshape(-1, 18))
    
    env.render()
