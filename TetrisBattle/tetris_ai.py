import os
from stable_baselines import PPO2

import random
from .settings import *

CASE_NAME = "ppo2_tetris_test"

class TetrisAI():
    def __init__(self):

        self.model = None

        if os.path.isfile(CASE_NAME + ".zip"):
            self.model = PPO2.load(CASE_NAME)
        
    def set_env(self, env):
        self.env = env
        
    def get_obs(self, time):
        grid = self.env.get_grid()
        grid[-1][-1] = time / MAX_TIME
        return grid.flatten()

    def predict(self, time):
        if self.model is None:
            return self.env.random_action()
        
        obs = self.get_obs(time)

        action, _states = self.model.predict(obs)
        return action
