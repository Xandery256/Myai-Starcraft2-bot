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
First, choose the faction you wish to fight against. Go to Myai.py and change the Computer's race to Terran, Zerg, or Protoss (line 478). Then in load-train-model.py, LOAD_MODEL contains the path for the AI model to be used. Depending on the Faction you wish to compete against you will set LOAD_MODEL to the following path:
* Protoss
  * models/trainingProtoss/50000.zip
* Terran
  * models/trainingTerran/50000.zip
* Zerg
  * models/trainingZerg/50000.zip
Next, run load-train-model.py file. This will launch the game and start the AI with a semi-optimized algorithm. The AI will continue to play and train itself until the script is terminated (Ctrl+C).
