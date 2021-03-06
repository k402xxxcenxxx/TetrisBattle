from TetrisBattle.envs.tetris_env import TetrisSingleEnv

import gym
import numpy as np

import pickle

from stable_baselines.common.policies import MlpPolicy
from stable_baselines import PPO2
from stable_baselines.common import make_vec_env
from stable_baselines.common.callbacks import BaseCallback
from stable_baselines import results_plotter
from stable_baselines.bench import Monitor
from stable_baselines.results_plotter import load_results, ts2xy
from stable_baselines.common.noise import AdaptiveParamNoiseSpec
import os

class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).

    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: (int)
    """
    def __init__(self, check_freq: int, log_dir: str, verbose=1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'diff_grid_model')
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:
            tmp_path = os.path.join(self.save_path, "%d.pkl" % self.n_calls)
            with open(tmp_path, 'wb') as outfile:
                params = self.model.get_parameters()
                pickle.dump(params, outfile)
            tmp_path = os.path.join(self.save_path, "%d" % self.n_calls)
            self.model.save(tmp_path)
            if self.verbose > 0:
            	print("Saving {}th model to {}".format(self.n_calls, tmp_path))

        return True

# Create log dir
log_dir = "tmp/"
os.makedirs(log_dir, exist_ok=True)

env = make_vec_env(TetrisSingleEnv, n_envs=16, env_kwargs={"gridchoice": "comboking", "obs_type": "diff_grid", "mode": "rgb_array"})

# Create the callback: check every 1000 steps
callback = SaveOnBestTrainingRewardCallback(check_freq=1000, log_dir=log_dir)
# Train the agent
time_steps = 1e12
model = PPO2(MlpPolicy, env, verbose=1, nminibatches=4, tensorboard_log="./ppo2_tetris_diff_grid_tensorboard/")
model.learn(total_timesteps=int(time_steps), callback=callback)
model.save("ppo2_tetris")

del model # remove to demonstrate saving and loading

model = PPO2.load("ppo2_tetris")

obs = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()
