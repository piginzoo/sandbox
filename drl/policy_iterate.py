import numpy as np
import random
from gym import spaces
import gym
from gym.envs.classic_control import rendering

#模拟环境类
class GridWorldEnvPolicyIterate(gym.Env):
    #相关的全局配置
    metadata = {
        'render.modes':['human', 'rgb_array'],
        'video.frames_per_second': 2
    }

    def __init__(self):
        self.states = [i for i in range(1, 37)] #初始化状态
        self.terminate_states = [3, 7, 11, 15, 19, 20, 23, 30,  33, 34] #终结态
        self.actions = ['up', 'down', 'left', 'right'] #动作空间

        self.v_states = dict() #状态的值空间
        for state in self.states:
            self.v_states[state] = 0.0

        for state in self.terminate_states: #先将所有陷阱和黄金的值函数初始化为-1.0
            self.v_states[state] = -1.0

        self.v_states[34] = 1.0  #黄金的位置值函数初始化为 1

        self.initStateAction() #初始化每个状态的可行动作空间
        self.initStatePolicyAction() #随机初始化当前策略

        self.gamma = 0.8 #计算值函数用的折扣因子
        self.viewer = None #视图对象
        self.current_state = None #当前状态
        return

    def translateStateToRowCol(self, state):
        """
        将状态转化为行列坐标返回
        """
        row = (state - 1) // 6
        col = (state - 1) %  6
        return row, col

    def translateRowColToState(self, row, col):
        """
        将行列坐标转化为状态值
        """
        return row * 6 + col + 1

    def actionRowCol(self, row, col, action):
        """
        对行列坐标执行动作action并返回坐标
        """
        if action == "up":
            row = row - 1
        if action == "down":
            row = row + 1
        if action == "left":
            col = col - 1
        if action == "right":
            col = col + 1
        return row, col

    def canUp(self, row, col):
        row = row - 1
        return 0 <= row <= 5

    def canDown(self, row, col):
        row = row + 1
        return 0 <= row <= 5

    def canLeft(self, row, col):
        col = col - 1
        return 0 <= col <= 5

    def canRight(self, row, col):
        col = col + 1
        return 0 <= col <= 5

    def initStateAction(self):
        """
        初始化每个状态可行动作空间
        """
        self.states_actions = dict()
        for state in self.states:
            self.states_actions[state] = []
            if state in self.terminate_states:
                continue
            row, col = self.translateStateToRowCol(state)
            if self.canUp(row, col):
                self.states_actions[state].append("up")
            if self.canDown(row, col):
                self.states_actions[state].append("down")
            if self.canLeft(row, col):
                self.states_actions[state].append('left')
            if self.canRight(row, col):
                self.states_actions[state].append('right')
        return


    def initStatePolicyAction(self):
        """
        初始化每个状态的当前策略动作
        """
        self.states_policy_action = dict()
        for state in self.states:
            if state in self.terminate_states:
                self.states_policy_action[state] = None
            else:
                #这个是随机选择一个，当做这个策略的初始值，也就是每个s上给他随机初始化一个action
                self.states_policy_action[state] = random.sample(self.states_actions[state], 1)[0]
        return


    def seed(self, seed = None):
        random.seed(seed)
        return [seed]

    def reset(self):
        """
        重置原始状态
        """
        self.current_state = random.sample(self.states, 1)[0]

    def step(self, action):
        """
        动作迭代函数
        """
        cur_state = self.current_state
        if cur_state in self.terminate_states:
            return cur_state, -1, True, {}
        row, col = self.translateStateToRowCol(cur_state)
        n_row, n_col = self.actionRowCol(row, col, action)
        next_state = self.translateRowColToState(n_row, n_col)
        self.current_state = next_state
        if next_state == 34:
            print ("找到黄金：34")
            return next_state,1,True,{}

        if next_state in self.terminate_states:
            return next_state, -1, True, {}
        else:
            return next_state, 0, False, {}

    def policy_evaluate(self):
        """
        策略评估过程 
        """
        error = 0.000001 #误差率
        for _ in range(1000):
            max_error = 0.0 #初始化最大误差
            for state in self.states:
                if state in self.terminate_states:
                    continue
                action = self.states_policy_action[state]#按照s找到对应的action，注意，这里用的是上一次policy_improve更新了策略（也就是s对应的a）
                self.current_state = state
                next_state, reward, isTerminate, info = self.step(action)#执行根据策略来的action对应，得到下个状态s和它对应的reward
                old_value = self.v_states[state]
                self.v_states[state] = reward + self.gamma * self.v_states[next_state]#算V(s),是下一状态的V_next(s)*gamma + reward
                abs_error = abs(self.v_states[state] - old_value)
                max_error = abs_error if abs_error > max_error else max_error #更新最大值
            if max_error < error:
                break
        i=0
        for state in self.states:
            print("%0.2f," % self.v_states[state],end='')
            i+=1
            if i>=6: 
                i=0
                print(" .")
        print ("====================")   

    def policy_improve(self):
        """
        根据策略评估的结果，进行策略更新,并返回每个状态的当前策略是否发生了变化
        """
        changed = False
        for state in self.states:
            if state in self.terminate_states:
                continue
            max_value_action = self.states_actions[state][0] #当前最大值行为
            max_value = -1000000000000.0 #当前最大回报 
            for action in self.states_actions[state]:#这里注意，states_actions[state]里面是这个status所有的可选动作，有多个
                self.current_state = state
                next_state, reward, isTerminate, info = self.step(action)#试着走一下
                q_reward = reward + self.gamma * self.v_states[next_state]#然后算他的Q(s,a)
                if q_reward > max_value:#看是不是这个status里面最大的按个Q(s,a)
                    max_value_action = action
                    max_value = q_reward
            if self.states_policy_action[state] != max_value_action:
                changed = True
            self.states_policy_action[state] = max_value_action#最大的那个Q(S,a)作为这个状态的应该选择的action，这里是更新了策略，这个s对应的action，看这个是一个确定action
        return changed





    def createGrids(self):
        """
        创建网格
        """
        start_x = 40
        start_y = 40
        line_length = 40
        for state in self.states:
            row, col = self.translateStateToRowCol(state)
            x = start_x + col * line_length
            y = start_y + row * line_length
            line = rendering.Line((x, y), (x + line_length, y))
            line.set_color(0, 0, 0)
            self.viewer.add_onetime(line)
            line = rendering.Line((x, y), (x, y  + line_length))
            line.set_color(0, 0, 0)
            self.viewer.add_onetime(line)
            line = rendering.Line((x + line_length, y), (x + line_length, y  + line_length))
            line.set_color(0, 0, 0)
            self.viewer.add_onetime(line)
            line = rendering.Line((x, y + line_length), (x + line_length, y  + line_length))
            line.set_color(0, 0, 0)
            self.viewer.add_onetime(line)

    def createTraps(self):
        """
        创建陷阱,将黄金的位置也先绘制成陷阱，后面覆盖画成黄金
        """
        start_x = 40 
        start_y = 40
        line_length = 40
        for state in self.terminate_states:
            row, col = self.translateStateToRowCol(state)
            trap = rendering.make_circle(20)
            trans = rendering.Transform()
            trap.add_attr(trans)
            trap.set_color(0, 0, 0)
            trans.set_translation(start_x + line_length * col + 20, start_y + line_length * row + 20)
            self.viewer.add_onetime(trap)

    def createGold(self):
        """
        创建黄金
        """
        start_x = 40 
        start_y = 40
        line_length = 40
        state = 34
        row, col = self.translateStateToRowCol(state)
        gold = rendering.make_circle(20)
        trans = rendering.Transform()
        gold.add_attr(trans)
        gold.set_color(1, 0.9, 0)
        trans.set_translation(start_x + line_length * col + 20, start_y + line_length * row + 20)
        self.viewer.add_onetime(gold)

    def createRobot(self):
        """
        创建机器人
        """
        start_x = 40 
        start_y = 40
        line_length = 40
        row, col = self.translateStateToRowCol(self.current_state)
        robot = rendering.make_circle(15)
        trans = rendering.Transform()
        robot.add_attr(trans)
        robot.set_color(1, 0, 1)
        trans.set_translation(start_x + line_length * col + 20, start_y + line_length * row + 20)
        self.viewer.add_onetime(robot)

    def render(self, mode="human", close=False):
        """
        渲染整个场景
        """
        #关闭视图
        if close:
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None

        #视图的大小
        screen_width = 320
        screen_height = 320


        if self.viewer is None:
            self.viewer = rendering.Viewer(screen_width, screen_height)

        #创建网格
        self.createGrids()
        #创建陷阱
        self.createTraps()
        #创建黄金
        self.createGold()
        #创建机器人
        self.createRobot()
        return self.viewer.render(return_rgb_array= mode == 'rgb_array')
