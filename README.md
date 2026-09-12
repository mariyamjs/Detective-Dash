# Detective-Dash
Redesigned the Google Dinosaur Game using SCAMPER principles to create Detective Dash, an original game developed in Python.
<img width="1362" height="698" alt="image" src="https://github.com/user-attachments/assets/1cae81e5-33e5-488c-83fe-ab79da38497a" />

Detective Dash is a three-level game developed in Python using Pygame. The project started with the Google Dinosaur Game as the original concept, and we used the SCAMPER design process to transform it into a detective and mystery-solving game.

The game consists of three levels, with each level representing a different murder mystery. As the player moves through a level, they avoid obstacles and collect clues that provide information about the crime.

At the end of each level, the player uses the clues they collected to solve the mystery by selecting the correct:

- Suspect
- Location
- Murder weapon

The player only moves on to the next level if all three selections are correct. If the mystery is solved correctly, the next case is unlocked with a new setting, clues, and gameplay mechanics.

## How the Game Works

Each level follows the same overall investigation process:

1. Play through the level and avoid obstacles.
2. Collect clues throughout the level.
3. Use the clues to figure out what happened.
4. Select the suspect, location, and murder weapon.
5. Solve all three parts of the mystery correctly to unlock the next level.

This made clue collection an important part of the gameplay rather than something that was only used for scoring. The player has to pay attention to the clues because they are needed to solve each case.

## Game Levels

### Level 1 - The Investigation Begins


The first level is the closest to the original Google Dinosaur Game. The player controls the detective and runs through the level while jumping over household objects and collecting clues.

The clues provide information about the first murder mystery. Once the player reaches the end, they use the clues they collected to identify the correct suspect, location, and murder weapon.

All three answers must be correct before the player can continue to Level 2.
<img width="1362" height="768" alt="image" src="https://github.com/user-attachments/assets/ab35ac94-7826-4c84-85a5-f34ecb635085" />

<img width="1362" height="761" alt="image" src="https://github.com/user-attachments/assets/25fec1e7-4773-4884-a650-4391690fde00" />


### Level 2 - Train Chase

The second level introduces a completely new murder mystery along with a different environment and gameplay style.

This level takes inspiration from Subway Surfers. The detective moves through a train environment, running across trains, jumping between them, avoiding gaps and obstacles, and collecting clues along the way.

At the end of the level, the player is presented with another set of suspects, locations, and weapons. They have to use the clues from this level to correctly solve the second murder before Level 3 is unlocked.

<img width="1353" height="751" alt="image" src="https://github.com/user-attachments/assets/ad7a56fa-c00a-4d65-91fd-9702581c9fd7" />
<img width="1362" height="772" alt="image" src="https://github.com/user-attachments/assets/bb262e67-4b30-43b5-9fcf-139f24aee8ae" />


### Level 3 - Final Pursuit

The third level introduces the final murder mystery and changes the gameplay mechanics again.

This level takes inspiration from Flappy Bird. Instead of mainly running and jumping, the player controls the detective's vertical movement while moving forward and avoiding obstacles.

Clues are collected throughout the level and are used to solve the final case. At the end, the player must once again determine the correct suspect, location, and murder weapon based on the clues they found.

<img width="1371" height="766" alt="image" src="https://github.com/user-attachments/assets/283bf485-0281-48bf-9c2e-a3a36ebdcd84" />
<img width="1358" height="773" alt="image" src="https://github.com/user-attachments/assets/45460889-2a97-48ce-ade4-91e05b5c68b3" />

## Mystery and Clues

<img width="1363" height="768" alt="image" src="https://github.com/user-attachments/assets/22efcffc-3f1e-49bf-a686-21482174a139" />

Each of the three levels contains its own separate murder mystery.

The clues collected in one level relate specifically to that level's case. Once the gameplay portion of the level is complete, the player has to interpret those clues and make three decisions: who committed the murder, where the murder took place, and which weapon was used.

The mystery acts as the progression system for the game. Completing the running or obstacle section alone is not enough to move forward. The player also has to correctly solve the case.

This was one of the main ways we changed the original Google Dinosaur Game. Instead of the goal being to survive for as long as possible and achieve a high score, Detective Dash gives the player a reason to collect information and use it to progress through the game.

<img width="1363" height="767" alt="image" src="https://github.com/user-attachments/assets/1885cd37-8d04-4294-b001-5f7ab2e1ddb5" />

## SCAMPER Design Process

We used SCAMPER to take the original Google Dinosaur Game and develop it into Detective Dash.

**Substitute:** We replaced the dinosaur with a detective and changed the original setting and obstacles.

**Combine:** We combined obstacle-based gameplay with clue collection and murder-mystery solving.

**Adapt:** We adapted gameplay ideas from Google Dinosaur, Subway Surfers, and Flappy Bird to create three different levels.

**Modify:** We changed the characters, environments, obstacles, objectives, and movement mechanics.

**Put to Another Use:** We used the endless-runner concept as the starting point for an investigation game where the player's actions help them solve a mystery.

**Eliminate:** We moved away from endless survival and high scores by introducing individual levels and murder cases that have to be solved.

**Reverse/Rearrange:** Instead of repeating the same gameplay throughout the game, each level changes the environment and mechanics while introducing a new case.

## Technologies Used

- Python
- Pygame
- Git/GitHub

## Main Features

- Three different murder mysteries
- Three levels with different gameplay mechanics
- Clue collection system
- Suspect, location, and weapon selection
- Mystery-solving system
- Level progression based on correct answers
- Player movement and jumping
- Collision detection
- Obstacles
- Multiple game environments

## What I Learned

This project gave me experience using Python and Pygame to build a game with multiple connected systems. Along with implementing player movement, obstacles, collision detection, and level progression, we had to connect the gameplay to the clue and mystery-solving system.

It also gave me experience using the SCAMPER design process to take an existing game concept and turn it into something different. Rather than recreating the Google Dinosaur Game, we used it as a starting point and added new gameplay styles, three separate mysteries, clue collection, and a system where solving each case determines whether the player can progress.

## How to Run

1. Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
```

2. Open the project folder:

```bash
cd Detective-Dash
```

3. Install Pygame if it is not already installed:

```bash
pip install pygame
```

4. Run the main Python file:

```bash
python YOUR_MAIN_FILE.py
```

## About the Project

Detective Dash was developed as an engineering design project using the SCAMPER design process. The goal was to take the basic idea behind the Google Dinosaur Game and turn it into a new game with different levels, mechanics, and an overall objective.
