# Shadow Detective

A noir detective game made with Python and pygame.

You play a detective in purple. Walk through rainy cities, hotels, trains and a circus, find clues, question suspects and catch the culprit, all while dodging the obstacles that move around every room. There are five cases, and each one is harder than the last.

---

## Requirements

| What | Version |
|---|---|
| Python | 3.8 or newer (tested with 3.9) |
| pygame | 2.0 or newer (tested with 2.6.1) |

Install pygame once:

```bash
pip3 install pygame
```

On Windows the command is usually `pip install pygame`.

The game needs no other files, images or sounds, because everything is drawn in code.

## How to start

Open a terminal in the folder that contains `game.py` and run:

```bash
python3 game.py
```

On Windows use `python game.py`. You can also open the file in Thonny, IDLE or VS Code and press **Run**.

---

## Controls

| Key | Action |
|---|---|
| Arrow keys | Walk around |
| Walk out at the left or right edge | Go through the door on that side |
| SPACE | Examine things, talk to people, use doors |
| 1 – 6 | Choose a question while talking |
| N | Notebook (all clues you found) |
| F | Case file (story, timeline, suspects) |
| A | Accuse a suspect |
| H | How to play |
| Esc | Menu (resume, how to play, restart case, exit to title screen) |
| Enter | Continue on the end screens |
| X | Exit to the title screen from an end screen |

The mouse also works for the buttons and for choosing suspects and evidence.

## How to play

1. **Read the case file.** It tells you what happened, what was stolen and who the suspects are.
2. **Explore** the rooms and press SPACE next to objects to examine them. Clues go into your notebook. Some things are locked, so find the key or the code first.
3. **Question the suspects.** New questions appear when you find new clues. Some people lie!
4. **Watch out** for the obstacles that move through the rooms. Every bump costs points.
5. **Accuse** (A) the culprit when you are sure, and pick the clues that prove it. Wrong accusations cost an attempt. If you run out of attempts, the culprit escapes.

## The five cases

| # | Case | Story | Obstacles | Difficulty |
|---|---|---|---|---|
| 1 | The Museum Heist | A famous painting disappears from the city museum. | 1 floor polisher | 3 clues, 1 piece of evidence, 3 attempts, clues glow |
| 2 | Blackout at Hotel Aurora | A diamond necklace is stolen during a blackout. | 2 luggage trolleys | 4 clues, 2 pieces of evidence, 3 attempts, faint glow |
| 3 | The Stolen Formula | A secret battery formula vanishes from a manor in a thunderstorm. | 2 guard dogs | 5 clues, 3 pieces of evidence, 2 attempts, no glow |
| 4 | Snowbound Express | A golden egg disappears from a train stuck in the snow. | 3 sliding suitcases | 6 clues, 3 pieces of evidence, 2 attempts, locked hatbox |
| 5 | Circus of Shadows | Someone cut the trapeze rope on opening night. | 4 bouncing circus balls | 7 clues, 3 pieces of evidence, only 1 attempt, locked locker |

## Score

| Event | Points |
|---|---|
| New clue | +100 |
| New question asked | +10 |
| Case solved | +500, plus 100 for every attempt left |
| Bumping into an obstacle | −50 |
| Wrong accusation | −100 |

Every case also gives up to 3 stars (3 = no mistakes). After the last case you get your final score and a rank: *Rookie Detective*, *Senior Inspector* or *Master Detective*. The high score is saved in `highscore.txt`.

---

## Project requirements

| Requirement | Where it is in the game |
|---|---|
| Welcome screen | Title screen with "PRESS ANY KEY TO START" |
| Player control | Arrow keys to walk, SPACE to interact, number keys for questions |
| Obstacles or enemies | Every case has its own obstacles that move by themselves (patrolling or bouncing) |
| Collisions | Bumping into an obstacle costs 50 points and pushes the player back |
| Score system | Points for clues, questions and solved cases; minus points for bumps and wrong accusations |
| Current score | Always shown at the top left, with "+100" / "−50" popping up over the player |
| End game screen | Final score, high score and buttons to play again or exit |
| Increasing difficulty | More and faster obstacles, more clues needed, fewer attempts, no glowing clues; a `pygame.time.Clock` keeps 60 FPS |
| Player visible in purple | The detective wears purple and stands on a glowing purple ring |
| Size of the screen | Fixed with the constants `WIDTH, HEIGHT = 960, 600` |

---

### Inside `game.py`

1. **Settings**: screen size, speed, points and colours
2. **Story data**: all five cases (`CASE_1` … `CASE_5`) with rooms, clues, suspects, dialogues, case files and obstacles
3. **Drawing functions**: people, obstacles, intro scenes
4. **`Game` class**: the game loop, input, rooms, notebook, accusing and all screens

## Write your own case

1. Copy one of the `CASE_…` dictionaries in the story data part and change the texts.
2. Every room needs a drawing function called `draw_<name>` in the `Game` class (see `draw_hall` as an example).
3. Add a `theme` (colours, floor, weather, obstacles) and a `story` (case file).
4. Add your case to the list `CASES = [...]`.

The comments at the top of the story data part explain every setting.