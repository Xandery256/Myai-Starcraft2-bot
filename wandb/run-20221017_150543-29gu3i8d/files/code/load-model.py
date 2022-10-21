from stable_baselines3 import PPO
import os
from sc2env import Sc2Env
import time
from wandb.integration.sb3 import WandbCallback
import wandb


LOAD_MODEL = "models/test_run7/200000.zip"
# Environment:
env = Sc2Env()

# load the model:
model = PPO.load(LOAD_MODEL, env=env)

model_name = f"test_run5"

models_dir = f"models/{model_name}/"
logdir = f"logs/{model_name}/"


conf_dict = {"Model": "load-v16s",
             "Machine": "Puget/Desktop/v18/2",
             "policy":"MlpPolicy",
             "model_save_name": model_name,
             "load_model": LOAD_MODEL
             }

run = wandb.init(
    project=f'SC2RLv1',
    entity="xander_",
    config=conf_dict,
    sync_tensorboard=True,  # auto-upload sb3's tensorboard metrics
    save_code=True,  # save source code
)

# episodes = 5

# for ep in range(episodes):
#     obs = env.reset()
#     done = False
#     while not done:
#         action, _states = model.predict(obs)
#         obs, rewards, done, info = env.step(action)
#         env.render()
#         print(rewards)

# # further train:
# TIMESTEPS = 100000
# iters = 0
# # while True:
# print("On iteration: ", iters)
# iters += 1
# model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"PPO")
# 	# model.save(f"{models_dir}/{TIMESTEPS*iters}")