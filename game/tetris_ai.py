from .envs.tetris_env import TetrisSingleEnv
import random

class TetrisAI():
    def __init__(self, gridchoice="none", obs_type="image", mode="rgb_array"):
        self.env = TetrisSingleEnv(gridchoice, obs_type, mode)
        self.action_meaning = {
            0: "NOOP",
            1: "hold",
            2: "drop",
            3: "rotate_right",
            4: "rotate_left",
            5: "right",
            6: "left",
            7: "down"
        }
        self.n_actions = len(self.action_meaning)
        self.model = None

    def predict(self, obs=None):
        if self.model is None or obs is None:
            return self.env.random_action

        action, _states = model.predict(obs)
        return action
