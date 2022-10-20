file = open('results.txt', 'r')
Lines = file.readlines()
  
count = 0
wins = 0
losses = 0
# Strips the newline character
for line in Lines:
    count += 1
    line = line.strip()
    if(line.find("Victory") != -1):
        wins += 1
    elif(line.find("Defeat") != -1):
        losses += 1
print("Wins {} : Losses {}\n{}".format(wins, losses, wins/losses))