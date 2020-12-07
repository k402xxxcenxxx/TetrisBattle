import os
import abc
import numpy as np
import random

from TetrisBattle.settings import *

# from TetrisBattle.tetris import Tetris, Player, Judge, get_infos, freeze
from TetrisBattle.tetris_core import TetrisCore, Judge, get_infos

# from TetrisBattle.renderer import Renderer


POS_LIST = [
    {
        'combo': (44, 437),
        'tetris': (314, 477),
        'tspin': (304, 477),
        'back2back': (314, 437),
        'board': (112, 138),
        'drawscreen': (112, 138),
        'big_ko': (44, 235),
        'ko': (140, 233),
        'transparent': (110, 135),
        'gamescreen': (0, 0),
        'attack_clean': (298, 140, 3, 360),
        'attack_alarm': (298, 481, 3, 18)
    },
    {
        'combo': (415, 437),
        'tetris': (685, 477),
        'tspin': (675, 477),
        'back2back': (685, 437),
        'board': (495, 138),
        'drawscreen': (495, 138),
        'big_ko': (426, 235),
        'ko': (527, 233),
        'transparent': (494, 135),
        'gamescreen': (0, 0),
        'attack_clean': (680, 140, 3, 360),
        'attack_alarm': (680, 481, 3, 18)
    }
]

class ComEvent:
    '''
    IO for the AI-agent, which is simulated the pygame.event
    '''
    def __init__(self):
        self._pre_evt_list = []
        self._now_evt_list = []

    def get(self):
        return self._now_evt_list

    def set(self, actions):
        # action: list of int

        self._now_evt_list = []

        # for evt in self._pre_evt_list:
        #     if evt.type == pygame.KEYDOWN or evt.type == "HOLD":
        #         if evt.key not in actions:
        #         # if evt.key != action:
        #             self._now_evt_list.append(ComEvt(pygame.KEYUP, evt.key))

        # for action in actions:
        #     hold = 0
        #     for evt in self._pre_evt_list:
        #         if evt.key == action:
        #             if evt.type == pygame.KEYDOWN or evt.type == "HOLD":
        #                 hold = 1
        #                 self._now_evt_list.append(ComEvt("HOLD", action))
        #     if not hold:
        #         self._now_evt_list.append(ComEvt(pygame.KEYDOWN, action))

        # self._pre_evt_list = self._now_evt_list

    def reset(self):
        del self._pre_evt_list[:]
        del self._now_evt_list[:]

class ComEvt:
    '''
    class that score the key informations, it is used in ComEvent
    '''
    def __init__(self, type_, key_):
        self._type = type_
        self._key = key_

    @property
    def key(self):
        return self._key

    @property
    def type(self):
        return self._type

class TetrisInterface(abc.ABC):

    metadata = {'render.modes': ['human', 'rgb_array'],
                'obs_type': ['image', 'grid']}

    #######################################
    # observation type:
    # "image" => screen shot of the game
    # "grid"  => the row data array of the game

    def __init__(self, gridchoice="none", obs_type="image", mode="rgb_array"):

        if mode == "rgb_array":
            os.environ["SDL_VIDEODRIVER"] = "dummy"

        # self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) # SCREEN is 800*600

        images = load_imgs()

        # self.renderer = Renderer(self.screen, images)

        self._obs_type = obs_type

        self._mode = mode

        self.time = MAX_TIME
        self.last_fallen_time = MAX_TIME

        self._action_meaning = {
            0: "NOOP",
            1: "hold",
            2: "drop",
            3: "rotate_right",
            4: "rotate_left",
            5: "right",
            6: "left",
            7: "down"
        }

        self._n_actions = len(self._action_meaning)

        # print(self.action_space.n)

        self._action_set = list(range(self._n_actions))

        self.repeat = 1 # emulate the latency of human action

        # self.myClock = pygame.time.Clock() # this will be used to set the FPS(frames/s)

        # self.timer2p = pygame.time.Clock() # this will be used for counting down time in our game

        self.tetris_list = []
        self.num_players = -1
        self.now_player = -1

        self.ob_memory = []
        self.init_ob_memory()
        self.is_fallen = 0

        # whether to fix the speed cross device. Do this by
        # fix the FPS to FPS (100)
        self._fix_speed_cross_device = True
        self._fix_fps = FPS

    @property
    def action_meaning(self):
        return self._action_meaning

    @property
    def n_actions(self):
        return self._n_actions

    @property
    def action_set(self):
        return self._action_set

    def screen_size(self):
        # return (x, y)
        return [SCREENHEIGHT, SCREENWIDTH]

    def get_screen_shot(self):
        pass
        # ob = pygame.surfarray.array3d(pygame.display.get_surface())
        # ob = np.transpose(ob, (1, 0, 2))
        # return ob

    def init_ob_memory(self):
        if self._obs_type == "grid":
            grid_1 = np.zeros(GRID_DEPTH * (GRID_WIDTH + 8))
            grid_1.fill(0)

            self.ob_memory.append(grid_1)
            self.ob_memory.append(grid_1)
        elif self._obs_type == "diff_grid":
            grid_1 = np.zeros(GRID_WIDTH)
            grid_1.fill(0)

            self.ob_memory.append(grid_1)
            self.ob_memory.append(grid_1)
        elif self._obs_type == "image":
            pass

    def _get_seen_grid(self):
        grid_1 = self.tetris_list[self.now_player]["tetris"].get_grid()
        grid_1[-1][-1] = self.time / MAX_TIME
        return grid_1.flatten()
        # return self.tetris_list[self.now_player]["tetris"].get_grid().reshape(GRID_DEPTH, GRID_WIDTH, 1)

    def get_seen_grid(self):
        #self.ob_memory.pop(0)

        #grid_1 = self._get_seen_grid()
        #self.ob_memory.append(grid_1)

        #grid = np.concatenate(self.ob_memory, axis=0)

        #return grid
        return self.tetris_list[self.now_player]["tetris"].get_grid().reshape(GRID_DEPTH, GRID_WIDTH, 1)

    def _get_diff_grid(self):
        grid_1 = self.tetris_list[self.now_player]["tetris"].get_diff_grid()
        return grid_1.flatten()

    def get_diff_grid(self):
        self.ob_memory.pop()

        grid_1 = self._get_diff_grid()
        self.ob_memory.append(grid_1)

        grid = np.concatenate(self.ob_memory, axis=0)

        return grid

    def get_obs(self):
        if self._obs_type == "grid":
            return self.get_seen_grid()
        elif self._obs_type == "image":
            img = self.get_screen_shot()
        elif self._obs_type == "diff_grid":
            return self.get_diff_grid()
        return img

    def random_action(self):
        return random.randint(0, self._n_actions - 1)

    def getCurrentPlayerID(self):
        return self.now_player

    def take_turns(self):
        self.now_player += 1
        self.now_player %= self.num_players
        return self.now_player

    def reward_func(self, infos):
        # define the reward function based on the given infos
        raise NotImplementedError

    def update_time(self, _time):
        # update the time clock and return the running state

        if self._fix_speed_cross_device:
            time_per_while = 1 / self._fix_fps * 1000 # transform to milisecond
        else:
            time_per_while = self.timer2p.tick()      # milisecond

        if _time >= 0:
            _time -= time_per_while * SPEED_UP
        else:
            _time = 0

        return _time

    def task_before_action(self, player):
        # set up the clock and curr_repeat_time
        # set the action to last_action if curr_repeat_time != 0

        # self.timer2p.tick() # start calculate the game time
        player["curr_repeat_time"] += 1
        player["curr_repeat_time"] %= self.repeat

    def get_true_action(self, player, action):
        if player["curr_repeat_time"] != 0:
            action = player["last_action"]

        player["last_action"] = action

        return action

    def reset(self):
        # Reset the state of the environment to an initial state

        self.time = MAX_TIME
        self.last_fallen_time = MAX_TIME
        self.now_player = random.randint(0, self.num_players - 1)
        self.total_reward = 0
        self.curr_repeat_time = 0 # denote the current repeat times
        self.last_infos = {'height_sum': 0,
                           'diff_sum': 0,
                           'max_height': 0,
                           'holes': 0,
                           'n_used_block': 0}
        self.n_used_block = 0

        for i, player in enumerate(self.tetris_list):
            if i + 1 > self.num_players:
                break
            tetris = player["tetris"]
            com_event = player["com_event"]
            pos = player["pos"]
            player["curr_repeat_time"] = 0
            player["last_action"] = 0
            tetris.reset()

            com_event.reset()
            # self.renderer.drawByName("gamescreen", pos["gamescreen"][0], pos["gamescreen"][1]) # blitting the main background

            # self.renderer.drawGameScreen(tetris)

        # self.renderer.drawTime2p(self.time)

        #time goes until it hits zero
        #when it hits zero return endgame screen

        # pygame.display.flip()
        # self.myClock.tick(FPS)

        height_sum, diff_sum, max_height, holes = get_infos(tetris.get_board())
        self.last_infos["height_sum"] = height_sum
        self.last_infos["diff_sum"] = diff_sum
        self.last_infos["max_height"] = max_height
        self.last_infos["holes"] = holes

        ob = self.get_obs()

        return ob


class TetrisSingleInterface(TetrisInterface):

    metadata = {'render.modes': ['human', 'rgb_array'],
                'obs_type': ['image', 'grid']}

    #######################################
    # observation type:
    # "image" => screen shot of the game
    # "grid"  => the row data array of the game

    def __init__(self, gridchoice="none", obs_type="image", mode="rgb_array"):
        super(TetrisSingleInterface, self).__init__(gridchoice, obs_type, mode)
        self.num_players = 1
        self.mode = mode

        for i in range(self.num_players + 1):
            info_dict = {"id": i}

            # adding the action information
            for k, v in self._action_meaning.items():
                info_dict[v] = k

            self.tetris_list.append({
                'info_dict': info_dict,
                'tetris': TetrisCore(gridchoice),
                'com_event': ComEvent(),
                'pos': POS_LIST[i],
                'curr_repeat_time': 0,
                'last_action': 0
            })

        self.reset()

    def heuristic_reward(self, infos):
        aggregate_height = infos['height_sum']
        complete_lines = infos['cleared']
        holes = infos['holes']
        bumpiness = infos['diff_sum']
        return -0.510066 * aggregate_height + 0.760666 * complete_lines + -0.35663 * holes + -0.184483 * bumpiness

    def reward_func(self, infos):
        if infos['is_fallen']:
            # basic_reward = infos['n_used_block'] * 0.001 # + infos['scores']
            # time_reward = 3 * max(0, min((2500 - infos['wait_time'])/2500, 1))
            # additional_reward = 10 * infos['cleared']  
            # panelty = 1.0 * infos['holes'] + 1.0 * infos['max_height'] + 1.0 * infos['height_sum'] + 1.0 * infos['diff_sum']
            
            # hard_drop_bonus = 2 if infos['action'] == 2 else 1 

            # reward = hard_drop_bonus * (basic_reward + additional_reward - panelty + time_reward)
            # return reward
            return self.heuristic_reward(infos)
        return 0.0
        #if infos['is_fallen']:
        #    basic_reward = infos['scores']
        #    # additional_reward = 0.01 if infos['holes'] == 0 else 0

        #    additional_reward = -1 * infos['max_height'] + 10 * infos['cleared'] - 0.5 * infos['holes'] - 0.1 * infos['diff_sum']
        #    # additional_reward = 0.76 * infos['cleared'] - 0.1* infos['height_sum']
        #    # additional_reward = infos['cleared'] # + (0.2 if infos['holes'] == 0 else 0)
        #    # return basic_reward + 0.01 * additional_reward - infos['penalty']
        #    return basic_reward + 1 * additional_reward + infos['reward_notdie']

        #return 0
    def act(self, action):
        # Execute one time step within the environment

        end = 0
        scores = 0

        player, opponent = self.tetris_list[self.now_player], self.tetris_list[::-1][self.now_player]
        tetris = player["tetris"]
        com_event = player["com_event"]
        pos = player["pos"]

        self.task_before_action(player)

        action = self.get_true_action(player, action)

        tetris.natural_down()

        if action == 0:
            pass
        elif action == 1:
            tetris.hold()
        elif action == 2:
            tetris.hardDrop()
        elif action == 3:
            tetris.rotate(_dir=1)
        elif action == 4:
            tetris.rotate(_dir=-1)
        elif action == 5:
            tetris.move_right()
        elif action == 6:
            tetris.move_left()
        elif action == 7:
            tetris.move_down()

        # tetris.move()

        # np.set_printoptions(precision=1)
        # print(tetris.get_grid()[:20, :10])
        # print(tetris.get_diff_grid())

        scores = 0

        penalty_die = 0

        reward_notdie = 0

        if tetris.collideDown():

            if self.last_fallen_time >= FALL_DOWN_FREQ:
                self.is_fallen = 1
                # put_block_in_grid(self.grid, self.block, self.px, self.py)
                tetris.put_block_in_grid()

                # compute the scores and attack the opponent
                # scores = tetris.clear()
                self.cleared, bomb_cleared = tetris.get_cleared()

                if tetris.check_KO():
                    tetris.clear_garbage()

                    penalty_die = self.total_reward * 0.8

                    end = 1

                tetris.new_block()
            else:
                self.last_fallen_time -= self.update_time(0)

            # print(self.last_fallen_time)
        else:
            self.last_fallen_time = 0

        # if tetris.KO > 0:
        #     pass

        self.time = self.update_time(self.time)

        if self.time == 0:
            reward_notdie = 0.3 * self.total_reward
            end = 1

        ob = self.get_obs()

        infos = {'is_fallen': self.is_fallen}

        if self.is_fallen:
            self.n_used_block = self.n_used_block + 1

            height_sum, diff_sum, max_height, holes = get_infos(tetris.get_board())

            # store the different of each information due to the move
            infos['height_sum'] = height_sum - self.last_infos['height_sum'] - 4
            infos['diff_sum'] =  diff_sum - self.last_infos['diff_sum']
            infos['max_height'] =  max_height - self.last_infos['max_height']
            infos['holes'] =  holes - self.last_infos['holes']
            infos['is_fallen'] =  self.is_fallen
            # infos['scores'] =  scores
            infos['cleared'] =  self.cleared
            infos['penalty'] =  penalty_die
            infos['reward_notdie'] = reward_notdie

            infos['n_used_block'] = self.n_used_block
            infos['wait_time'] = self.last_fallen_time - self.time
            infos['action'] = action

            self.last_infos = {'height_sum': height_sum,
                               'diff_sum': diff_sum,
                               'max_height': max_height,
                               'holes': holes,
                               }
            
            self.last_fallen_time = self.time

            # if holes > 2:
            #     # print("Too bad, end early!")
            #     end = 1

        # if self.last_fallen_time - self.time > 2500:
            # end = 1
            # print("Too slow, end early!")
            # print(infos)

        reward = self.reward_func(infos)

        self.total_reward += reward

        # if end:
        #     # freeze(0.5)
        #     infos['sent'] = tetris.sent
        #     # self.reset()

        return ob, reward, end, infos

class TetrisDoubleInterface(TetrisInterface):

    metadata = {'render.modes': ['human', 'rgb_array'],
                'obs_type': ['image', 'grid']}

    #######################################
    # observation type:
    # "image" => screen shot of the game
    # "grid"  => the row data array of the game

    def __init__(self, gridchoice="none", obs_type="image", mode="rgb_array"):
        super(TetrisDoubleInterface, self).__init__(gridchoice, obs_type, mode)

        self.num_players = 2

        for i in range(self.num_players):
            info_dict = {"id": i}

            # adding the action information
            for k, v in self._action_meaning.items():
                info_dict[v] = k

            self.tetris_list.append({
                'info_dict': info_dict,
                # 'tetris': Tetris(Player(info_dict), gridchoice, mode!="human"),
                'tetris': TetrisCore(gridchoice),
                'com_event': ComEvent(),
                'pos': POS_LIST[i]
            })
        self.reset()

    def reward_func(self, infos):
        if infos.get('winner') is not None:
            # if you are winner, the reward is 1
            # if you are loser, the reward is -1
            return (infos['winner'] == infos['now_player'] - 0.5) * 2

        return 0

    def act(self, action):
        # Execute one time step within the environment

        end = 0
        scores = 0

        player, opponent = self.tetris_list[self.now_player], self.tetris_list[::-1][self.now_player]
        tetris = player["tetris"]
        com_event = player["com_event"]
        pos = player["pos"]

        self.task_before_action(player)

        action = self.get_true_action(player, action)

        tetris.natural_down()

        com_event.set([action])

        for evt in com_event.get():
            tetris.trigger(evt)

        tetris.move()

        scores = 0

        if tetris.check_fallen():
            # compute the scores and attack the opponent
            scores = tetris.clear()

            opponent["tetris"].add_attacked(scores)

            # self.renderer.drawCombo(tetris, *pos["combo"])

            # self.renderer.drawTetris(tetris, *pos["tetris"])
            # self.renderer.drawTspin(tetris, *pos["tspin"])
            # self.renderer.drawBack2Back(tetris, *pos["back2back"])

            if tetris.check_KO():

                # self.renderer.drawBoard(tetris, *pos["board"])

                opponent["tetris"].update_ko()

                tetris.clear_garbage()

                # self.renderer.drawByName("ko", *pos["ko"])
                # self.renderer.drawByName("transparent", *pos["transparent"])

                # screen.blit(kos[tetris_2.get_KO() - 1], (426, 235))
                # pygame.display.flip()

                # scores -= 1

                # end = 1

            tetris.new_block()

        # self.renderer.drawGameScreen(tetris)

        tetris.increment_timer()

        # if tetris.attacked == 0:
        #     pygame.draw.rect(self.screen, (30, 30, 30), pos["attack_clean"])

        if tetris.attacked != 0:

            for j in range(tetris.attacked):
                pos_attack_alarm = list(pos["attack_alarm"])
                # modified the y axis of the rectangle, according to the strength of attack
                pos_attack_alarm[1] = pos_attack_alarm[1] - 18 * j
                # pygame.draw.rect(self.screen, (255, 0, 0), pos_attack_alarm)

        if tetris.KO > 0:
            pass
            # self.renderer.drawKO(tetris.KO, *pos["big_ko"])

        # self.renderer.drawScreen(tetris, *pos["drawscreen"])

            # SCREEN.blit(IMAGES["transparent"], (494, 135))

        if Judge.check_ko_win(tetris, max_ko=3):
            end = 1
            winner = tetris.get_id()

        if Judge.check_ko_win(opponent["tetris"], max_ko=3):
            end = 1
            winner = opponent["tetris"].get_id()

        self.time = self.update_time(self.time)

        if self.time == 0:
            winner = Judge.who_win(tetris, opponent["tetris"])
            end = 1

        # self.renderer.drawTime2p(self.time)

        # self.myClock.tick(FPS)
        # pygame.display.flip()

        ob = self.get_obs()

        infos = {'now_player': self.now_player}

        if end:
            # freeze(0.5)
            print(winner)

            infos['winner'] = winner

            # self.reset()

        reward = self.reward_func(infos)

        return ob, reward, end, infos
