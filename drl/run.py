import gym
from grid_world_env import GridWorldEnv
from gym.envs.registration import register
try:
    register(id = "GridWorld-v3", entry_point=GridWorldEnv, max_episode_steps = 200, reward_threshold=100.0)
except:
    pass

from time import sleep
env = gym.make('GridWorld-v3')
env.reset()

#策略评估和策略改善 
not_changed_count = 0
for _ in range(10000):
    env.env.policy_evaluate()
    changed = env.env.policy_improve()
    if changed:
        not_changed_count = 0
    else:
        not_changed_count += 1
    if not_changed_count == 10: #超过10次策略没有再更新，说明策略已经稳定了
        break
print("策略评估完成")

#观察env到底是个什么东西的打印信息。
print(isinstance(env, GridWorldEnv))
print(type(env))
print(env.__dict__)
print(isinstance(env.env, GridWorldEnv))

env.reset()

for _ in range(1000):
    env.render()
    if env.env.states_policy_action[env.env.current_state] is not None:
        observation,reward,done,info = env.step(env.env.states_policy_action[env.env.current_state])
    else:
        done = True
    print(_)
    if done:
        sleep(0.5)
        env.render()
        env.reset()
        print("reset")
    sleep(0.5)
env.close()
