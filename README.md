# Myai-Starcraft2-bot

## Setting up the Ai
* Install StarCraft II
* Copy the Maps folder into the StarCraft II folder
* Run the following commands using python 3.9:
  * pip install --upgrade burnysc2
  * pip install torch
  * pip install stable-baselines3
  * pip install wandb
  * pip install tensorboard
* Create a wandb account
  * Replace the project name with a project name of your choice
  * Replace the entity name with your wandb username

## Running the Ai
First, choose the faction and difficulty you wish to fight against. Go to Myai.py and change the Computer's race to Terran, Zerg, or Protoss and the Computer's difficulty to Easy, Medium, or Hard (line 478). Next, go to train.py and set the model_name to the faction you selected (e.g. trainingZerg). To start training the AI, run train.py. The AI will continue to play and train itself until the script is terminated (Ctrl+C).

## Loading a Model
If the Ai has been training for some time, run tensorboard --logdir /logs/folder/ with the faction folder you are training. Open the Tensorboard link and look at the ep_rew_mean graph. Find the Ai's peak performance and the corresponding step value (x-axis). In load-train-model.py, LOAD_MODEL contains the path for the AI model to be used. Depending on the Faction you wish to compete against you will set LOAD_MODEL to the folder and model that is closest to the Ai's peak performance. Next, run load-train-model.py file. This will launch the game and start the AI with a semi-optimized algorithm. The AI will continue to play and train itself until the script is terminated (Ctrl+C).

