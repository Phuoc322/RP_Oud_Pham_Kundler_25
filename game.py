"""
Shadow Detective - a small point-and-click detective game made with pygame.

Five cases, each one harder than the last. Everything is in this one file:
the story data of all cases comes first, then the drawing code and the game.

Controls:
  Arrow keys - walk around (walk out at the left / right edge to change rooms)
  SPACE      - examine things, talk to people, use doors
  1 - 6      - choose a question when talking
  N          - open / close the notebook
  A          - accuse a suspect
  F          - read the case file
  H          - how to play
  Esc        - menu (pause, restart, title screen, exit)

Watch out for moving obstacles: bumping into one costs 50 points.

Run:  pip install pygame   then   python3 shadow_detective.py
"""
import math
import os
import random
import sys

import pygame

# The screen size is fixed - everything is drawn for 960 x 600 pixels
WIDTH, HEIGHT = 960, 600
FPS = 60                     # the clock keeps the game at 60 frames per second
TOP_BAR = 50
FLOOR_Y = 430

# Player and scoring
PLAYER_PURPLE = (128, 62, 196)
PLAYER_SPEED = 300           # pixels per second
PLAYER_TOP, PLAYER_BOTTOM = 448, 588
POINTS_CLUE = 100
POINTS_QUESTION = 10
POINTS_SOLVED = 500
POINTS_HIT = -50
POINTS_WRONG = -100
HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.txt")

# Colours: the world is mostly grey - clues and accents get colour
BLACK = (8, 8, 10)
DARK = (18, 18, 22)
FLOOR_LINE = (40, 42, 47)
GREY = (90, 92, 98)
LIGHT_GREY = (150, 152, 158)
WHITE = (232, 232, 232)
PAPER = (232, 221, 190)
INK = (40, 32, 24)
WOOD = (62, 48, 36)
WOOD_DARK = (40, 30, 22)
BRASS = (170, 135, 70)
GOLD = (212, 164, 58)
YELLOW = (255, 217, 119)
RED = (230, 45, 60)
ORANGE = (255, 138, 31)
GREEN_LIGHT = (110, 220, 140)
BULB_COLORS = [(255, 90, 90), (255, 210, 90), (110, 220, 140), (110, 170, 255), (230, 120, 255)]

HOW_TO_PLAY = [
    ("Move", "You are the purple detective. Walk with the ARROW KEYS. Walk out at the "
             "left or right edge of a room to go through the door there."),
    ("Examine and talk", "Stand next to something and press SPACE to examine it or to "
                         "talk to a person. Clues go into your notebook (N). Some things "
                         "are locked - find the key or the code first!"),
    ("Watch out!", "Things move around in every room. Bumping into them costs 50 "
                   "points and pushes you back. Every case gets faster and more crowded."),
    ("Score", "New clue +100, new question +10, solved case +500 plus 100 for every "
              "attempt left. A wrong accusation costs 100 points."),
    ("Accuse", "When you are sure, press A. Choose the culprit and the clues that "
               "prove it. Each wrong accusation costs one attempt."),
]


# ==========================================================================
# STORY DATA - all five cases.
#
# Every case is a dictionary. To write your own case, copy one of them and
# change the texts. Rooms are drawn by the functions draw_<name> in
# shadow_detective.py (the "draw" entry of each room).
#
# Difficulty settings per case:
#   min_clues  - clues you must find before you may accuse someone
#   evidence   - how many clues you must pick when accusing
#   attempts   - wrong accusations allowed
#   glow       - how strongly clues glow (1 = strong, 0 = not at all)
#
# A spot can be locked: give it "needs": <clue id> and a "locked" text.
# It only reveals its clue after the needed clue has been found.
#
# The look of every case is set in its "theme" (see the end of this part).
# ==========================================================================

# Extra colours used by the cases
BLUE = (70, 110, 170)
PURPLE = (130, 80, 160)
ICE = (170, 215, 255)
PINK = (215, 95, 150)
CYAN = (80, 190, 200)
GREEN = (90, 180, 110)
SILVER = (185, 185, 195)

LEFT_DOOR = (40, 230, 110, 200)
RIGHT_DOOR = (810, 230, 110, 200)


# ==========================================================================
# CASE 1 - The Museum Heist (easy)
# ==========================================================================

CASE_1 = {
    "title": "The Museum Heist",
    "question": "Who stole The Moonlit Night?",
    "intro": "Rain hammers the city of Greyhaven. At 22:30 your phone rings: The "
             "Moonlit Night, the most valuable painting in the city museum, has "
             "been stolen. Four people were in the building. One of them is lying.",
    "min_clues": 3, "evidence": 1, "attempts": 3, "glow": 1.0,
    "start": "hall",
    "rooms": {
        "hall": {
            "name": "Entrance Hall", "draw": "hall", "wall": (46, 48, 54),
            "doors": [{"rect": LEFT_DOOR, "sign": "OFFICE", "to": "office"},
                      {"rect": RIGHT_DOOR, "sign": "EXHIBITION", "to": "exhibition"}],
            "people": [("ole", 700, 550, False)],
            "spots": [
                {"rect": (185, 170, 160, 90), "label": "Key board", "clue": "key", "color": RED},
                {"rect": (620, 160, 120, 90), "label": "Camera control panel",
                 "clue": "camera", "color": YELLOW},
                {"rect": (400, 190, 160, 240), "label": "Main entrance",
                 "look": ("Main Entrance", "The front doors are locked from the inside. "
                          "Nobody broke in - the thief was already in the building.")},
                {"rect": (170, 395, 220, 70), "label": "Reception desk",
                 "look": ("Reception Desk", "A stack of brochures: 'Home of The Moonlit "
                          "Night - insured, protected, priceless.'")},
            ],
        },
        "exhibition": {
            "name": "Exhibition Room", "draw": "exhibition", "wall": (50, 50, 56),
            "doors": [{"rect": LEFT_DOOR, "sign": "HALL", "to": "hall"},
                      {"rect": RIGHT_DOOR, "sign": "STORAGE", "to": "storage", "ajar": True}],
            "people": [("leon", 260, 550, False)],
            "spots": [
                {"rect": (460, 425, 340, 110), "label": "Footprints", "clue": "footprints",
                 "color": ORANGE},
                {"rect": (380, 110, 200, 170), "label": "Empty frame",
                 "look": ("Empty Frame", "The Moonlit Night is gone. Only a nail and a "
                          "dusty outline remain.")},
                {"rect": (350, 300, 260, 110), "label": "Velvet rope",
                 "look": ("Velvet Rope", "The rope was cut cleanly. The thief came prepared.")},
                {"rect": (180, 120, 120, 150), "label": "Portrait",
                 "look": ("Old Portrait", "A grim old man in a grey suit. He looks like he "
                          "knows something. He doesn't.")},
                {"rect": (640, 120, 110, 90), "label": "Landscape",
                 "look": ("Grey Landscape", "A grey landscape. Still here. Apparently not "
                          "worth stealing.")},
            ],
        },
        "office": {
            "name": "Director's Office", "draw": "office", "wall": (52, 48, 46),
            "doors": [{"rect": (820, 230, 110, 200), "sign": "HALL", "to": "hall"}],
            "people": [("weber", 430, 452, True)],
            "spots": [
                {"rect": (495, 335, 90, 45), "label": "Papers", "clue": "contract", "color": RED},
                {"rect": (330, 360, 340, 100), "label": "Desk",
                 "look": ("Desk", "A tidy desk. Very tidy. Almost too tidy.")},
                {"rect": (80, 110, 180, 170), "label": "Window",
                 "look": ("Window", "Rain. The window is locked from the inside.")},
                {"rect": (560, 130, 90, 110), "label": "Photo",
                 "look": ("Photo", "Director Weber at the museum gala, wearing her famous "
                          "bright red lipstick.")},
                {"rect": (690, 320, 100, 110), "label": "Safe",
                 "look": ("Safe", "The safe is open. Inside: unpaid bills. Lots and lots "
                          "of unpaid bills.")},
            ],
        },
        "storage": {
            "name": "Storage Room", "draw": "storage", "wall": (38, 38, 42),
            "doors": [{"rect": LEFT_DOOR, "sign": "EXHIBITION", "to": "exhibition"}],
            "people": [("karl", 560, 550, False)],
            "spots": [
                {"rect": (345, 312, 42, 42), "label": "Coffee cup", "clue": "cup", "color": RED},
                {"rect": (690, 225, 100, 100), "label": "Something behind the crates",
                 "clue": "painting", "color": GOLD},
                {"rect": (250, 395, 75, 40), "label": "Boots",
                 "look": ("Work Boots", "Karl's spare work boots. Enormous - size 45.")},
                {"rect": (175, 290, 70, 145), "label": "Mop and bucket",
                 "look": ("Mop and Bucket", "Karl's mop. The bucket is full of clean water.")},
                {"rect": (640, 320, 190, 115), "label": "Crates",
                 "look": ("Crates", "Old crates full of plaster statues.")},
            ],
        },
    },
    "clues": {
        "footprints": ("Muddy Footprints",
                       "Small muddy footprints, shoe size 38. They lead from the empty "
                       "frame straight to the storage room."),
        "key": ("Missing Key",
                "The hook labelled STORAGE on the key board is empty. Someone took the "
                "storage room key."),
        "camera": ("Camera Log",
                   "The camera was switched off from 22:10 to 22:20 with the admin "
                   "password. Only Director Weber and guard Ole know it."),
        "contract": ("Insurance Contract",
                     "The painting's insurance was raised from 200,000 to 2,000,000 - "
                     "just last week. Signed: H. Weber."),
        "cup": ("Lipstick Cup",
                "A coffee cup, still warm, with a red lipstick mark on the rim. Someone "
                "was in here only minutes ago."),
        "painting": ("Hidden Painting",
                     "Behind the crates, wrapped in a blanket: The Moonlit Night! The "
                     "painting never left the building."),
    },
    "culprit": "weber",
    "strong": ["footprints", "camera", "contract", "cup"],
    "weak_text": {
        "key": "Weber shrugs: 'Anyone in this building could have taken that key.' "
               "That alone proves nothing.",
        "painting": "Weber gasps: 'You found it! But that doesn't tell you who hid it.' "
                    "You need evidence that points to her.",
    },
    "confession": "Director Weber confesses!",
    "solution": "Director Weber was broke. Last week she raised the insurance to "
                "2,000,000. At 22:05 she sent Ole up to the roof, switched off the "
                "camera with her password, took the storage key and hid the painting "
                "behind the crates - leaving lipstick on a coffee cup and size 38 "
                "footprints on the floor. After the insurance paid, she wanted to sell "
                "the painting in secret.",
    "suspects": {
        "karl": {
            "name": "Karl", "role": "Janitor", "style": "karl", "accent": BLUE,
            "greeting": "Evening, detective. Mind the wet floor.",
            "topics": [
                {"q": "Where were you tonight?",
                 "a": "Mopping the basement, like every night. Ask my mop, it'll tell you."},
                {"q": "What about the footprints?", "req": "footprints",
                 "a": "Not mine, detective! I wear size 45 boots. Those tiny prints come "
                      "from a fancy shoe."},
                {"q": "Did you take the storage key?", "req": "key",
                 "a": "Why would I? I carry my own key ring. I haven't touched that board "
                      "in years."},
                {"q": "Is this your coffee cup?", "req": "cup",
                 "a": "Me? I only drink tea. And I don't wear lipstick, ha!"},
                {"q": "What do you think of the director?",
                 "a": "Coffee, coffee, coffee. She leaves cups with red lipstick all over "
                      "my clean museum!"},
            ],
            "innocent": "Karl's boots are size 45 - far too big for the footprints. And "
                        "he doesn't even know the camera password. Karl is innocent.",
        },
        "weber": {
            "name": "Helga Weber", "role": "Museum Director", "style": "weber", "accent": RED,
            "greeting": "Detective! Thank goodness. Please, find my painting.",
            "topics": [
                {"q": "Where were you tonight?",
                 "a": "In my office all evening, doing paperwork. I never left, I swear."},
                {"q": "Who knows the camera password?", "req": "camera",
                 "a": "Only me... and Ole, the guard. If I were you, I'd take a closer "
                      "look at him."},
                {"q": "Why was the insurance raised?", "req": "contract",
                 "a": "Pure coincidence! The painting has, um, gained value. The art "
                      "market, you know."},
                {"q": "Were you in the storage room?", "req": "cup",
                 "a": "The storage room? Never! I don't even drink coffee."},
                {"q": "Does the museum have money trouble?",
                 "a": "The museum is doing perfectly fine. Next question, please."},
            ],
            "innocent": "",
        },
        "leon": {
            "name": "Leon", "role": "Artist", "style": "leon", "accent": PURPLE,
            "greeting": "Ah, the detective. Here to admire art, or to blame the artist?",
            "topics": [
                {"q": "Where were you tonight?",
                 "a": "I came at 21:00 to see my rival's painting one last time. I left at "
                      "21:30 - the guard let me out."},
                {"q": "You hated the painter, right?",
                 "a": "Hate? He copied my style! But stealing his painting would only make "
                      "him more famous. No, thank you."},
                {"q": "What about the footprints?", "req": "footprints",
                 "a": "Size 38? Please. I wear 43. Big feet, big talent."},
            ],
            "innocent": "Ole locked the door behind Leon at 21:30, but the painting "
                        "vanished after 22:10. Leon is innocent.",
        },
        "ole": {
            "name": "Ole", "role": "Security Guard", "style": "ole", "accent": YELLOW,
            "greeting": "Detective. I didn't see anything... well, almost nothing.",
            "topics": [
                {"q": "Where were you tonight?",
                 "a": "Doing my rounds. At 22:15 I was up on the roof. When I came back "
                      "down, the frame was empty."},
                {"q": "Why were you on the roof?",
                 "a": "The director called me at 22:05. She said the roof alarm was "
                      "beeping. But it wasn't beeping at all..."},
                {"q": "Who switched off the camera?", "req": "camera",
                 "a": "Not me! The control panel is down here, and I was on the roof. Only "
                      "the director and I know the password."},
                {"q": "Did you see Leon tonight?",
                 "a": "Yes, he left at 21:30. I locked the door behind him myself."},
                {"q": "I heard you have gambling debts.",
                 "a": "...It's true. But I'm trying to quit. I would never steal. I love "
                      "this job."},
            ],
            "innocent": "Ole was on the roof when the camera was switched off - the "
                        "director sent him there. Ole is innocent.",
        },
    },
}


# ==========================================================================
# CASE 2 - Blackout at Hotel Aurora (medium)
# ==========================================================================

CASE_2 = {
    "title": "Blackout at Hotel Aurora",
    "question": "Who stole the Ice Star?",
    "intro": "Hotel Aurora, 23:00. In the middle of the Countess's party, every light "
             "in the hotel goes out. Five minutes of darkness. When the lights come "
             "back, her diamond necklace, the Ice Star, is gone from its glass case.",
    "min_clues": 4, "evidence": 2, "attempts": 3, "glow": 0.45,
    "start": "lobby",
    "rooms": {
        "lobby": {
            "name": "Hotel Lobby", "draw": "lobby", "wall": (58, 50, 44),
            "doors": [{"rect": LEFT_DOOR, "sign": "BALLROOM", "to": "ballroom"},
                      {"rect": RIGHT_DOOR, "sign": "KITCHEN", "to": "kitchen"}],
            "people": [("finch", 420, 440, True), ("countess", 250, 550, False)],
            "spots": [
                {"rect": (515, 312, 85, 40), "label": "Book on the desk", "clue": "keylog",
                 "color": GOLD},
                {"rect": (555, 175, 130, 80), "label": "Key rack",
                 "look": ("Key Rack", "Every key is back on its hook - including the "
                          "basement key. Whoever borrowed it brought it back.")},
                {"rect": (330, 345, 300, 85), "label": "Reception desk",
                 "look": ("Reception Desk", "A brass bell and a vase of white lilies. "
                          "Very elegant.")},
                {"rect": (180, 110, 110, 130), "label": "Portrait",
                 "look": ("Portrait", "Aurora Valdez, founder of the hotel, 1902. She "
                          "looks disappointed in all of you.")},
            ],
        },
        "ballroom": {
            "name": "Ballroom", "draw": "ballroom", "wall": (44, 40, 52),
            "doors": [{"rect": RIGHT_DOOR, "sign": "LOBBY", "to": "lobby"}],
            "people": [("mia", 150, 550, False)],
            "spots": [
                {"rect": (370, 285, 75, 50), "label": "Inside the piano", "clue": "recorder",
                 "color": RED},
                {"rect": (330, 425, 60, 30), "label": "Under the bench", "clue": "clasp",
                 "color": ICE},
                {"rect": (240, 270, 250, 150), "label": "Grand piano",
                 "look": ("Grand Piano", "A shiny black grand piano. The lid is open.")},
                {"rect": (620, 270, 100, 165), "label": "Display case",
                 "look": ("Empty Display Case", "The lock was opened, not broken. The Ice "
                          "Star lay on this velvet cushion until 23:00.")},
                {"rect": (540, 100, 100, 140), "label": "Window",
                 "look": ("Window", "Closed and locked. The thief didn't come from "
                          "outside.")},
            ],
        },
        "kitchen": {
            "name": "Hotel Kitchen", "draw": "kitchen", "wall": (60, 62, 60),
            "doors": [{"rect": LEFT_DOOR, "sign": "LOBBY", "to": "lobby"},
                      {"rect": RIGHT_DOOR, "sign": "BASEMENT", "to": "fuseroom"}],
            "people": [("bruno", 480, 550, False)],
            "spots": [
                {"rect": (282, 308, 56, 36), "label": "Glove", "clue": "glove",
                 "color": WHITE},
                {"rect": (712, 340, 64, 95), "label": "Rubbish bin", "clue": "letter",
                 "color": WHITE},
                {"rect": (190, 150, 170, 60), "label": "Shelf",
                 "look": ("Timer Shelf", "A row of egg timers. One of them is missing.")},
                {"rect": (555, 315, 150, 115), "label": "Stove",
                 "look": ("Stove", "Pots of soup, still bubbling. Smells amazing.")},
                {"rect": (360, 455, 90, 40), "label": "Cake on the floor",
                 "look": ("Ruined Cake", "A three-layer chocolate cake, dropped in the "
                          "dark. A tragedy.")},
            ],
        },
        "fuseroom": {
            "name": "Fuse Room", "draw": "fuseroom", "wall": (36, 38, 40),
            "doors": [{"rect": LEFT_DOOR, "sign": "KITCHEN", "to": "kitchen"}],
            "people": [],
            "spots": [
                {"rect": (500, 248, 70, 64), "label": "Something on the fuse box",
                 "clue": "timer", "color": ORANGE},
                {"rect": (585, 455, 85, 45), "label": "Paper on the floor", "clue": "sheet",
                 "color": WHITE},
                {"rect": (410, 150, 160, 175), "label": "Fuse box",
                 "look": ("Main Fuse Box", "The main switch for the whole hotel. Someone "
                          "flipped it off - and later back on.")},
                {"rect": (700, 190, 100, 240), "label": "Boiler",
                 "look": ("Boiler", "An old boiler. It rumbles like a grumpy bear.")},
            ],
        },
    },
    "clues": {
        "recorder": ("Tape Recorder",
                     "Hidden inside the piano: a tape recorder with the Moonlight Sonata on "
                     "it. The piano music in the dark was a recording!"),
        "clasp": ("Broken Clasp",
                  "Under the piano bench: a broken silver clasp from the Ice Star "
                  "necklace."),
        "keylog": ("Key Log",
                   "The key log at reception: 'Basement key - borrowed 19:10 - M. Rossi.' "
                   "Mia Rossi is the pianist."),
        "timer": ("Egg Timer",
                  "An egg timer from the kitchen is wired to the main switch. It was set "
                  "for exactly 23:00 - the blackout was planned."),
        "sheet": ("Sheet Music",
                  "A torn page of sheet music on the basement floor. Pencil notes in the "
                  "corner, signed 'M.'"),
        "glove": ("Flour Glove",
                  "A white glove covered in flour, lying on the kitchen counter."),
        "letter": ("Bank Letter",
                   "A crumpled letter in the bin: the bank demands that Manager Finch pays "
                   "back 50,000 by Friday."),
    },
    "culprit": "mia",
    "strong": ["recorder", "clasp", "keylog", "sheet"],
    "weak_text": {
        "timer": "The timer proves the blackout was planned - but not who planned it. "
                 "Anyone could walk into the kitchen.",
        "glove": "Every cook in this hotel has flour on their gloves. That proves nothing.",
        "letter": "Money trouble is a motive, not a proof.",
    },
    "confession": "Mia Rossi confesses!",
    "solution": "Mia stole an egg timer from the kitchen, borrowed the basement key at "
                "19:10 and wired the timer to the main switch - dropping a page of her "
                "sheet music. At 23:00 the lights went out, and a tape recorder in the "
                "piano kept 'playing' for her. In the dark she grabbed the Ice Star, but "
                "the clasp broke and fell under the piano bench.",
    "suspects": {
        "countess": {
            "name": "Countess Valentina", "role": "Owner of the Ice Star", "style": "countess",
            "accent": CYAN,
            "greeting": "Darling detective, my Ice Star! Find it, I beg you!",
            "topics": [
                {"q": "What happened tonight?",
                 "a": "At 23:00 the lights went out. Five minutes of darkness! When they "
                      "came back, the glass case was open and empty."},
                {"q": "Did you hear anything in the dark?",
                 "a": "Only that lovely piano music. Mia played the whole time - without "
                      "one single mistake. In complete darkness!"},
                {"q": "Is the necklace insured?",
                 "a": "Insured? Darling, I never insure anything. I trust people."},
                {"q": "Is this clasp from your necklace?", "req": "clasp",
                 "a": "Yes! That's from my Ice Star! Where did you find it?"},
            ],
            "innocent": "Why would the Countess steal her own necklace? It wasn't even "
                        "insured. She is innocent.",
        },
        "finch": {
            "name": "Mr. Finch", "role": "Hotel Manager", "style": "manager", "accent": RED,
            "greeting": "Welcome to the Aurora! Please, keep this quiet. Our reputation!",
            "topics": [
                {"q": "Where were you during the blackout?",
                 "a": "Right here at the desk with a candle, calming the guests. At least "
                      "ten people saw me."},
                {"q": "Who can go into the fuse room?",
                 "a": "Staff only. Anybody else has to borrow the key here and sign the "
                      "key log."},
                {"q": "Did anything strange happen today?",
                 "a": "The piano came back from the tuner this morning. The movers said it "
                      "was heavier than usual."},
                {"q": "You owe the bank money?", "req": "letter",
                 "a": "...Yes. Times are hard. But I would never rob my own guests!"},
            ],
            "innocent": "Finch stood at the desk with a candle during the whole blackout - "
                        "ten guests saw him. He is innocent.",
        },
        "bruno": {
            "name": "Bruno", "role": "Chef", "style": "chef", "accent": ORANGE,
            "greeting": "Out of my kitchen! ...Oh, a detective. Fine. Be quick.",
            "topics": [
                {"q": "Where were you during the blackout?",
                 "a": "Here, with my three cooks. We dropped a whole cake in the dark. A "
                      "tragedy!"},
                {"q": "Did anyone come into the kitchen today?",
                 "a": "Mia, the pianist. At 19:00 she asked me how to get to the basement. "
                      "Strange question for a pianist."},
                {"q": "Is this your glove?", "req": "glove",
                 "a": "Of course! It's covered in flour - I'm a chef. I lost it this "
                      "morning."},
                {"q": "Is this egg timer from your kitchen?", "req": "timer",
                 "a": "Looks like one of mine. One went missing yesterday. Anyone can walk "
                      "in here."},
            ],
            "innocent": "Bruno was in the kitchen with three cooks during the blackout. "
                        "He is innocent.",
        },
        "mia": {
            "name": "Mia Rossi", "role": "Pianist", "style": "pianist", "accent": PINK,
            "greeting": "Shh... can't you see I'm practising?",
            "topics": [
                {"q": "Where were you during the blackout?",
                 "a": "At the piano, of course. I played the Moonlight Sonata in the dark. "
                      "Everyone heard me."},
                {"q": "Why did you borrow the basement key?", "req": "keylog",
                 "a": "Basement key? Oh, um... I was looking for the bathroom."},
                {"q": "What is this recorder in your piano?", "req": "recorder",
                 "a": "That's... for recording my practice. Lots of pianists do that!"},
                {"q": "Is this your sheet music?", "req": "sheet",
                 "a": "Lots of people play music. Lots of names start with M."},
            ],
            "innocent": "",
        },
    },
}


# ==========================================================================
# CASE 3 - The Stolen Formula (hard)
# ==========================================================================

CASE_3 = {
    "title": "The Stolen Formula",
    "question": "Who stole the formula?",
    "intro": "A thunderstorm over Ravenwood Manor. Professor Ada Ravenwood has invented "
             "a battery that could change the world. During her dinner party, the "
             "formula vanished from the safe in her laboratory. Five guests. One thief. "
             "And this time, someone wants you to blame the wrong person.",
    "min_clues": 5, "evidence": 3, "attempts": 2, "glow": 0.0,
    "start": "dining",
    "rooms": {
        "dining": {
            "name": "Dining Room", "draw": "dining", "wall": (60, 42, 40),
            "doors": [{"rect": LEFT_DOOR, "sign": "GREENHOUSE", "to": "greenhouse"},
                      {"rect": RIGHT_DOOR, "sign": "LIBRARY", "to": "library"}],
            "people": [("felix", 420, 450, True), ("hargreaves", 200, 550, False)],
            "spots": [
                {"rect": (620, 238, 75, 36), "label": "Notes on the sideboard",
                 "clue": "notes", "color": WHITE},
                {"rect": (625, 330, 50, 30), "label": "Ashtray",
                 "look": ("Ashtray", "At Mr. Crane's seat: a half-smoked cigar. It smells "
                          "of cherries.")},
                {"rect": (180, 360, 600, 75), "label": "Dinner table",
                 "look": ("Dinner Table", "Seven plates, half-eaten cake and melted "
                          "candles. Next to one plate there is a small empty space.")},
                {"rect": (300, 105, 100, 130), "label": "Portrait",
                 "look": ("Portrait", "Professor Ada Ravenwood. Her new battery could "
                          "power a whole city for a week.")},
            ],
        },
        "library": {
            "name": "Library", "draw": "library", "wall": (40, 46, 42),
            "doors": [{"rect": LEFT_DOOR, "sign": "DINING ROOM", "to": "dining"},
                      {"rect": RIGHT_DOOR, "sign": "LABORATORY", "to": "lab"}],
            "people": [("lily", 270, 550, False)],
            "spots": [
                {"rect": (435, 400, 75, 32), "label": "Paper in the fireplace",
                 "clue": "telegram", "color": ORANGE},
                {"rect": (528, 357, 52, 30), "label": "Camera", "clue": "photos",
                 "color": CYAN},
                {"rect": (590, 90, 190, 330), "label": "Bookshelf", "clue": "passage",
                 "color": GOLD},
                {"rect": (370, 250, 150, 180), "label": "Fireplace",
                 "look": ("Fireplace", "The fire is still warm. Someone burnt papers here "
                          "tonight.")},
                {"rect": (160, 90, 190, 330), "label": "Bookshelf",
                 "look": ("Bookshelf", "Books about electricity, magnets and... cake "
                          "recipes.")},
            ],
        },
        "lab": {
            "name": "Laboratory", "draw": "lab", "wall": (48, 54, 62),
            "doors": [{"rect": LEFT_DOOR, "sign": "LIBRARY", "to": "library"}],
            "people": [("nora", 520, 550, False)],
            "spots": [
                {"rect": (590, 438, 55, 28), "label": "Something shiny", "clue": "hairpin",
                 "color": GOLD},
                {"rect": (682, 440, 56, 28), "label": "Grey dust", "clue": "ash",
                 "color": SILVER},
                {"rect": (620, 250, 125, 145), "label": "Safe", "clue": "safe",
                 "color": GOLD},
                {"rect": (300, 105, 260, 135), "label": "Blackboard",
                 "look": ("Blackboard", "Formulas everywhere. One line says: 'Battery: 10x "
                          "stronger!' The rest is gibberish to you.")},
                {"rect": (150, 330, 300, 100), "label": "Lab bench",
                 "look": ("Lab Bench", "Flasks, wires and a half-eaten sandwich.")},
                {"rect": (790, 180, 110, 250), "label": "Strange machine",
                 "look": ("Strange Machine", "Copper coils that hum quietly. You decide "
                          "not to touch it.")},
            ],
        },
        "greenhouse": {
            "name": "Greenhouse", "draw": "greenhouse", "wall": (30, 40, 44),
            "doors": [{"rect": RIGHT_DOOR, "sign": "DINING ROOM", "to": "dining"}],
            "people": [("victor", 470, 550, False)],
            "spots": [
                {"rect": (655, 290, 80, 120), "label": "Behind the palm", "clue": "coat",
                 "color": GOLD},
                {"rect": (160, 300, 220, 130), "label": "Flower pots",
                 "look": ("Flower Pots", "Orchids, cactuses and one very sad tomato.")},
                {"rect": (600, 150, 170, 280), "label": "Palm tree",
                 "look": ("Palm Tree", "A huge palm. Its leaves are wet - somebody brushed "
                          "past it with a wet coat.")},
            ],
        },
    },
    "clues": {
        "safe": ("Open Safe",
                 "The safe was opened with the code, not forced. Only the professor, Nora "
                 "and Mr. Crane know the code."),
        "hairpin": ("Hairpin",
                    "A silver hairpin with the letter N, right in front of the safe. "
                    "Almost too easy to find..."),
        "ash": ("Cigar Ash",
                "Fresh cigar ash on the lab floor. It smells of cherries."),
        "telegram": ("Burnt Telegram",
                     "Half-burnt: '...SOLARCORP PAYS 1 MILLION FOR THE FORMULA. DELIVER "
                     "TONIGHT.' Addressed to: V. Crane."),
        "photos": ("Lily's Photos",
                   "Photos of the lab door, taken at 20:15 and 20:50. Both times the door "
                   "is closed and locked."),
        "passage": ("Secret Passage",
                    "One bookshelf slides aside: a secret passage to the laboratory! "
                    "That's how the thief got past the locked lab door."),
        "notes": ("Butler's Notes",
                  "Who left the table: 20:30 Felix (5 min). 20:40 Mr. Crane (15 min). "
                  "20:50 Nora (3 min, fetched dessert)."),
        "coat": ("Hidden Coat",
                 "A wet coat behind the palm. In the pocket: a train ticket for 06:00 "
                 "tomorrow. Name: V. Crane."),
    },
    "culprit": "victor",
    "strong": ["ash", "telegram", "notes", "coat"],
    "weak_text": {
        "safe": "Three people know the code. The open safe alone doesn't tell you which "
                "one it was.",
        "hairpin": "The hairpin points at Nora - not at the person you accused.",
        "photos": "The photos show the lab door was locked. Useful - but they don't "
                  "show the thief.",
        "passage": "The passage explains HOW the thief got in - not WHO it was.",
    },
    "confession": "Victor Crane confesses!",
    "solution": "Victor Crane sold the formula to SolarCorp for one million. At 20:40 he "
                "left the dinner and took Nora's hairpin from the table. He used the "
                "secret passage in the library, opened the safe with the code and dropped "
                "the hairpin to frame Nora - but the ash of his cherry cigar gave him "
                "away. He burnt the telegram and hid his wet coat with the train ticket "
                "in the greenhouse, ready to escape at 06:00.",
    "suspects": {
        "nora": {
            "name": "Nora Blake", "role": "Lab Assistant", "style": "labcoat", "accent": GREEN,
            "greeting": "Detective, please - the professor thinks I did it. I would never!",
            "topics": [
                {"q": "Who knows the safe code?",
                 "a": "Only the professor, me and Mr. Crane, her business partner."},
                {"q": "Where were you at 20:40?",
                 "a": "At the dinner table. At 20:50 I fetched dessert from the kitchen - "
                      "three minutes. The cook saw me."},
                {"q": "Is this your hairpin?", "req": "hairpin",
                 "a": "Yes! I took it off at dinner because it hurt. I left it next to my "
                      "plate. How did it get here?"},
                {"q": "Did you know about the passage?", "req": "passage",
                 "a": "A secret passage? No! I always use the normal lab door."},
            ],
            "innocent": "The hairpin was planted. Hargreaves saw it next to Nora's plate "
                        "until 20:45, and she only left the table for three minutes. "
                        "Nora was framed!",
        },
        "felix": {
            "name": "Felix", "role": "The Professor's Nephew", "style": "nephew",
            "accent": ORANGE,
            "greeting": "A stolen formula? Boring. Is there more cake?",
            "topics": [
                {"q": "Where were you at 20:40?",
                 "a": "On the phone in the hall from 20:30, five minutes. Then back to my "
                      "cake."},
                {"q": "Will you inherit everything one day?",
                 "a": "Maybe. But the formula is worth nothing to me. I can't even read "
                      "it."},
                {"q": "What do you think of Mr. Crane?",
                 "a": "Victor? Nervous all evening. He kept looking at his watch."},
            ],
            "innocent": "Felix was only gone for five minutes and doesn't know the safe "
                        "code. He is innocent.",
        },
        "hargreaves": {
            "name": "Mr. Hargreaves", "role": "Butler", "style": "butler", "accent": SILVER,
            "greeting": "Good evening. I have served the professor for thirty years. Ask me "
                        "anything.",
            "topics": [
                {"q": "Did anyone leave the dinner table?",
                 "a": "I keep notes of everything, sir. You'll find them on the sideboard."},
                {"q": "Who smokes in this house?",
                 "a": "Only Mr. Crane. Those dreadful cherry cigars."},
                {"q": "Did you hear anything strange?",
                 "a": "Thunder. And at 20:45 a creak from the library. Old houses creak, "
                      "sir."},
                {"q": "Did you see Nora's hairpin?", "req": "hairpin",
                 "a": "Indeed. It lay next to her plate. When I cleared the table at "
                      "20:45, it was gone."},
            ],
            "innocent": "The butler served dinner all evening in front of every guest. "
                        "He is innocent.",
        },
        "lily": {
            "name": "Lily Chen", "role": "Journalist", "style": "journalist", "accent": CYAN,
            "greeting": "Lily Chen, Daily Herald. Off the record? I didn't take it.",
            "topics": [
                {"q": "Why are you here?",
                 "a": "An interview with the professor about her new battery. Big story."},
                {"q": "Did you notice anything in here?",
                 "a": "At 20:45 I came in to look for a book. The whole room smelled of "
                      "cherries. Funny, right?"},
                {"q": "Why did you photograph the lab door?", "req": "photos",
                 "a": "For my article! Look at the times - the door was locked both "
                      "times."},
                {"q": "Did you know about this passage?", "req": "passage",
                 "a": "No! Wow. That's going on the front page."},
            ],
            "innocent": "Lily's own photos show the lab door stayed locked, and she didn't "
                        "know about the passage. She is innocent.",
        },
        "victor": {
            "name": "Victor Crane", "role": "Business Partner", "style": "partner",
            "accent": (200, 120, 60),
            "greeting": "Detective. Terrible business. Simply terrible.",
            "topics": [
                {"q": "Where were you at 20:40?",
                 "a": "I went out for some fresh air. Here in the greenhouse. The whole "
                      "time, I promise."},
                {"q": "Who knows the safe code?",
                 "a": "The professor, Nora and me. Nora has money problems, you know..."},
                {"q": "Do you smoke cherry cigars?", "req": "ash",
                 "a": "Who doesn't? A fine cigar. That proves nothing."},
                {"q": "What is this telegram?", "req": "telegram",
                 "a": "Never seen it. 'V. Crane'? Lots of people have that name."},
                {"q": "Is this your coat?", "req": "coat",
                 "a": "...My coat? Someone must have taken it by mistake."},
            ],
            "innocent": "",
        },
    },
}

# ==========================================================================
# CASE 4 - Snowbound Express (hard)
# ==========================================================================

CASE_4 = {
    "title": "Snowbound Express",
    "question": "Who stole the Emperor's Egg?",
    "intro": "The night train from Vienna to Venice is stuck in a snowstorm high in "
             "the Alps. At midnight the Emperor's Egg - a golden egg covered in jewels - "
             "vanished from the locked luggage car. The snow is three metres deep. "
             "Nobody could have left the train. The thief is still on board.",
    "min_clues": 6, "evidence": 3, "attempts": 2, "glow": 0.0,
    "start": "dining",
    "rooms": {
        "lounge": {
            "name": "Lounge Car", "draw": "lounge", "wall": (62, 40, 46),
            "doors": [{"rect": RIGHT_DOOR, "sign": "DINING CAR", "to": "dining"}],
            "people": [("odile", 520, 550, False)],
            "spots": [
                {"rect": (355, 368, 70, 32), "label": "Paper on the table", "clue": "program"},
                {"rect": (180, 345, 110, 50), "label": "Armchair", "clue": "telegram"},
                {"rect": (600, 300, 200, 130), "label": "Bar",
                 "look": ("Bar", "Bottles clink every time the wind shakes the train. "
                          "The barman went to bed hours ago.")},
                {"rect": (690, 240, 70, 60), "label": "Gramophone",
                 "look": ("Gramophone", "A record of Odile Fontaine singing La Traviata. "
                          "Signed by herself. Twice.")},
                {"rect": (245, 110, 170, 130), "label": "Window",
                 "look": ("Window", "Snow, snow and more snow. The mountains glow in the "
                          "moonlight.")},
            ],
        },
        "dining": {
            "name": "Dining Car", "draw": "train_dining", "wall": (72, 50, 36),
            "doors": [{"rect": LEFT_DOOR, "sign": "LOUNGE CAR", "to": "lounge"},
                      {"rect": RIGHT_DOOR, "sign": "SLEEPING CAR", "to": "sleeper"}],
            "people": [("baron", 300, 550, False), ("teo", 580, 550, False)],
            "spots": [
                {"rect": (680, 325, 70, 34), "label": "Serving cart", "clue": "order"},
                {"rect": (420, 318, 100, 30), "label": "Chess board",
                 "look": ("Chess Board", "The Baron's chess game. White is winning. So is "
                          "black. He plays against himself.")},
                {"rect": (180, 320, 160, 110), "label": "Table",
                 "look": ("Table", "Half a strudel and a cold cup of tea. Dr. Hassan "
                          "sat here at dinner.")},
                {"rect": (640, 110, 120, 120), "label": "Window",
                 "look": ("Window", "The snowstorm has buried the tracks. Nobody is "
                          "going anywhere tonight.")},
            ],
        },
        "sleeper": {
            "name": "Sleeping Car", "draw": "sleeper", "wall": (66, 50, 38),
            "doors": [{"rect": LEFT_DOOR, "sign": "DINING CAR", "to": "dining"},
                      {"rect": RIGHT_DOOR, "sign": "LUGGAGE CAR", "to": "luggage"}],
            "people": [("pavel", 230, 550, False), ("hassan", 520, 550, False)],
            "spots": [
                {"rect": (330, 318, 64, 44), "label": "Bag in compartment 2", "clue": "drops"},
                {"rect": (608, 312, 74, 56), "label": "Hatbox in compartment 4",
                 "clue": "egg", "needs": "program",
                 "locked": ("Hatbox", "A hatbox with a 4-digit combination lock. Maybe "
                            "its owner wrote her lucky number down somewhere...")},
                {"rect": (640, 432, 170, 48), "label": "Carpet", "clue": "heels"},
                {"rect": (165, 200, 120, 230), "label": "Compartment 1",
                 "look": ("Compartment 1", "Pavel's tiny compartment. A uniform, a timetable "
                          "and a photo of his cat.")},
                {"rect": (445, 200, 120, 230), "label": "Compartment 3",
                 "look": ("Compartment 3", "The Baron's compartment. Seven suitcases and "
                          "a golden toothbrush.")},
            ],
        },
        "luggage": {
            "name": "Luggage Car", "draw": "luggage", "wall": (52, 54, 58),
            "doors": [{"rect": LEFT_DOOR, "sign": "SLEEPING CAR", "to": "sleeper"}],
            "people": [],
            "spots": [
                {"rect": (676, 238, 40, 40), "label": "Something white", "clue": "feather"},
                {"rect": (262, 360, 44, 40), "label": "Cup", "clue": "cup"},
                {"rect": (640, 140, 90, 290), "label": "Cage door", "clue": "cage"},
                {"rect": (170, 300, 90, 130), "label": "Sleeping guard",
                 "look": ("Mr. Brandt", "The guard is fast asleep and snoring. Even shaking "
                          "him doesn't help.")},
                {"rect": (420, 250, 140, 150), "label": "Empty stand",
                 "look": ("Empty Stand", "A velvet stand inside the cage. This is where the "
                          "Emperor's Egg was.")},
                {"rect": (760, 100, 130, 100), "label": "Window",
                 "look": ("Open Window", "The window is wide open and snow blows in. But "
                          "there are no footprints in the snow outside.")},
            ],
        },
    },
    "clues": {
        "order": ("Order Slip",
                  "'23:30 - one hot chocolate with cream for the guard in the luggage car. "
                  "Paid by: compartment 4.'"),
        "program": ("Opera Program",
                    "A signed program: 'Odile Fontaine - my lucky year: 1896!' Someone "
                    "underlined 1-8-9-6 twice."),
        "telegram": ("Baron's Telegram",
                     "'Your offer for the Emperor's Egg is rejected. - Vienna Museum.' "
                     "Addressed to Baron von Greif."),
        "drops": ("Missing Drops",
                  "Dr. Hassan's medical bag. The bottle of strong sleeping drops is gone."),
        "heels": ("Wet Heel Prints",
                  "Small puddles of melted snow from high heels lead from the luggage car "
                  "to compartment 4."),
        "egg": ("Hidden Egg",
                "1-8-9-6 opens the hatbox. Under a wig: the Emperor's Egg! The hatbox "
                "belongs to compartment 4."),
        "cup": ("Hot Chocolate",
                "A cup next to the sleeping guard. It smells sweet - too sweet. Something "
                "was mixed into the chocolate."),
        "feather": ("White Feather",
                    "A white swan feather caught in the door of the luggage cage."),
        "cage": ("Opened Cage",
                 "The cage was unlocked, not broken. Somebody used the conductor's key."),
    },
    "culprit": "odile",
    "strong": ["order", "heels", "egg", "feather"],
    "weak_text": {
        "drops": "The drops belong to Dr. Hassan. That shows where they came from - not "
                 "who took them.",
        "cage": "The cage was opened with Pavel's key. But who had the key at 23:40?",
        "cup": "The cup shows HOW the guard fell asleep - not who drugged him.",
        "program": "A lucky number in a program proves nothing by itself.",
        "telegram": "A rejected offer is a motive, not a proof.",
    },
    "confession": "Odile Fontaine confesses!",
    "solution": "Odile Fontaine is deep in debt. At dinner she stole Dr. Hassan's "
                "sleeping drops. She ordered a hot chocolate for the guard and poured "
                "the drops in when Teo passed her in the corridor. At 23:40 she took "
                "Pavel's key from his belt, opened the cage and grabbed the egg - leaving "
                "a feather of her boa in the door. She opened the window so it would look "
                "like the thief escaped, walked back with snow on her heels and locked "
                "the egg in her hatbox with her lucky number. Then she 'found' Pavel's key.",
    "suspects": {
        "pavel": {
            "name": "Pavel", "role": "Conductor", "style": "conductor", "accent": GOLD,
            "greeting": "The Snowbound Express has never lost a passenger - or a parcel. "
                        "Until tonight.",
            "topics": [
                {"q": "Who has the luggage car key?",
                 "a": "Only me. It never leaves my belt. Well... at 23:40 I dropped it. "
                      "Madame Fontaine found it and gave it back. Such a kind lady."},
                {"q": "What happened at midnight?",
                 "a": "Mr. Brandt, the guard, didn't answer my knock. I found him asleep "
                      "and the cage open. The egg was gone."},
                {"q": "Can anyone leave the train?",
                 "a": "In this snow? Three metres deep! Whoever took it is still on board."},
                {"q": "The cage was opened with your key!", "req": "cage",
                 "a": "Impossible! It was on my belt the whole... oh. Oh no. The moment I "
                      "'dropped' it."},
            ],
            "innocent": "Pavel's key was taken from his belt at 23:40 - and Madame "
                        "Fontaine 'found' it. Pavel was tricked. He is innocent.",
        },
        "hassan": {
            "name": "Dr. Hassan", "role": "Doctor", "style": "doctor", "accent": (80, 150, 170),
            "greeting": "Doctor Amira Hassan. If anyone is hurt, I can help. Otherwise I'd "
                        "like to sleep.",
            "topics": [
                {"q": "Where were you at midnight?",
                 "a": "In my compartment, reading. The walls are thin. Around 00:05 I heard "
                      "someone walk past in high heels."},
                {"q": "Who sat next to you at dinner?",
                 "a": "Madame Fontaine. She asked many questions about my medicine. I "
                      "thought she was nervous about sleeping on a train."},
                {"q": "Your sleeping drops are missing.", "req": "drops",
                 "a": "Yes! I noticed it this evening. Someone took the bottle from my bag "
                      "in the dining car."},
                {"q": "Could this cup make a guard sleep?", "req": "cup",
                 "a": "That smell... yes. My sleeping drops. Ten drops and he sleeps for "
                      "hours."},
            ],
            "innocent": "Dr. Hassan's drops were stolen at dinner - and the person sitting "
                        "next to her was Madame Fontaine. Dr. Hassan is innocent.",
        },
        "teo": {
            "name": "Teo", "role": "Waiter", "style": "waiter", "accent": SILVER,
            "greeting": "Something to drink, sir? Sorry - I'm a bit nervous tonight.",
            "topics": [
                {"q": "Did you bring the guard anything?",
                 "a": "Yes, a hot chocolate at 23:30. A passenger paid for it. Very "
                      "generous!"},
                {"q": "Who paid for the chocolate?",
                 "a": "I don't remember the name. But it's on the order slip - on my "
                      "serving cart."},
                {"q": "Did you see anything strange?",
                 "a": "At 00:10 Madame Fontaine came in for a glass of water. The hem of "
                      "her dress was wet. Wet, on a train!"},
                {"q": "Did anyone touch the chocolate?", "req": "cup",
                 "a": "Only me! Well... Madame Fontaine stopped me in the corridor to smell "
                      "it. Just for a second."},
            ],
            "innocent": "Teo only carried the chocolate. The order slip shows who paid for "
                        "it. Teo is innocent.",
        },
        "baron": {
            "name": "Baron von Greif", "role": "Art Collector", "style": "baron",
            "accent": (200, 170, 80),
            "greeting": "Yes, I wanted the egg. No, I did not steal it. One buys - one "
                        "does not steal.",
            "topics": [
                {"q": "Where were you at midnight?",
                 "a": "Here, playing chess against myself. Teo can confirm. I won."},
                {"q": "Who else wanted the egg?",
                 "a": "Madame Fontaine asked me what it is worth. She seemed... very "
                      "interested. Opera singers earn less than you think."},
                {"q": "The museum rejected your offer?", "req": "telegram",
                 "a": "Annoying. But a collector who steals can never show his collection. "
                      "Pointless!"},
            ],
            "innocent": "The Baron played chess in the dining car all night - Teo saw him. "
                        "He is innocent.",
        },
        "odile": {
            "name": "Odile Fontaine", "role": "Opera Singer", "style": "singer",
            "accent": (235, 235, 235),
            "greeting": "Darling, are you here for an autograph? ...No? How disappointing.",
            "topics": [
                {"q": "Where were you at midnight?",
                 "a": "Asleep in compartment 4, of course. A voice like mine needs rest."},
                {"q": "You paid for the guard's chocolate.", "req": "order",
                 "a": "A kind gesture! The poor man was cold. Is kindness a crime now?"},
                {"q": "This feather is from your boa.", "req": "feather",
                 "a": "Lots of ladies wear feathers, darling."},
                {"q": "Wet heel prints lead to your door.", "req": "heels",
                 "a": "I... went to look at the snow. It's romantic. Is that forbidden?"},
                {"q": "Why is the egg in your hatbox?", "req": "egg",
                 "a": "Someone put it there! A trap! I'm innocent, darling!"},
            ],
            "innocent": "",
        },
    },
}


# ==========================================================================
# CASE 5 - Circus of Shadows (very hard)
# ==========================================================================

CASE_5 = {
    "title": "Circus of Shadows",
    "question": "Who cut the trapeze rope?",
    "intro": "Circus Lumiere, opening night. During the final act the trapeze rope "
             "snapped. Star acrobat Stella fell - straight into the safety net, unhurt. "
             "But the rope had been cut. Someone wanted the show to fail tonight. Six "
             "suspects, one saboteur - and only one chance to name them.",
    "min_clues": 7, "evidence": 3, "attempts": 1, "glow": 0.0,
    "start": "bigtop",
    "rooms": {
        "bigtop": {
            "name": "Big Top", "draw": "bigtop", "wall": (100, 38, 46), "wall2": (150, 136, 116),
            "doors": [{"rect": LEFT_DOOR, "sign": "BACKSTAGE", "to": "backstage"},
                      {"rect": RIGHT_DOOR, "sign": "CARAVANS", "to": "caravans"}],
            "people": [("krone", 470, 560, False), ("grey", 760, 550, False)],
            "spots": [
                {"rect": (662, 236, 46, 40), "label": "Rope ladder", "clue": "greasepaint"},
                {"rect": (515, 70, 60, 80), "label": "Snapped rope", "clue": "cutrope"},
                {"rect": (190, 372, 44, 28), "label": "Seat A1", "clue": "ticket"},
                {"rect": (330, 290, 300, 60), "label": "Safety net",
                 "look": ("Safety Net", "The net that saved Stella's life. Igor checks it "
                          "every day.")},
                {"rect": (160, 340, 140, 90), "label": "Front row",
                 "look": ("Front Row", "Popcorn everywhere. Someone left in a hurry.")},
            ],
        },
        "backstage": {
            "name": "Backstage", "draw": "backstage", "wall": (66, 52, 40),
            "doors": [{"rect": RIGHT_DOOR, "sign": "BIG TOP", "to": "bigtop"}],
            "people": [("pip", 150, 550, False), ("igor", 560, 550, False)],
            "spots": [
                {"rect": (378, 282, 52, 26), "label": "Knife", "clue": "knife"},
                {"rect": (255, 115, 160, 120), "label": "Make-up mirror", "clue": "mirror"},
                {"rect": (748, 160, 54, 270), "label": "Locker 7", "clue": "locker",
                 "needs": "lockerkey",
                 "locked": ("Locker 7", "Locked. A small sticker on the door shows a red "
                            "clown nose. You need the key.")},
                {"rect": (480, 130, 140, 200), "label": "Costume rack",
                 "look": ("Costume Rack", "Sequins, feathers, a lion costume... and a very "
                          "sad-looking unicorn.")},
                {"rect": (640, 160, 106, 270), "label": "Lockers 5 and 6",
                 "look": ("Lockers", "Igor's and Lia's lockers. Both open, both boring.")},
            ],
        },
        "fortune": {
            "name": "Fortune Teller's Tent", "draw": "fortune", "wall": (44, 26, 52),
            "doors": [{"rect": LEFT_DOOR, "sign": "CARAVANS", "to": "caravans"}],
            "people": [("zora", 480, 450, True)],
            "spots": [
                {"rect": (392, 360, 56, 22), "label": "Book on the table", "clue": "zorabook"},
                {"rect": (180, 115, 120, 160), "label": "Poster", "clue": "prediction"},
                {"rect": (455, 318, 52, 50), "label": "Crystal ball",
                 "look": ("Crystal Ball", "It glows softly. You see... your own nose. Very "
                          "mysterious.")},
                {"rect": (520, 360, 80, 25), "label": "Tarot cards",
                 "look": ("Tarot Cards", "The top card: THE TOWER. A tower struck by "
                          "lightning, people falling.")},
            ],
        },
        "caravans": {
            "name": "Caravans", "draw": "caravans", "wall": (14, 14, 34),
            "doors": [{"rect": LEFT_DOOR, "sign": "BIG TOP", "to": "bigtop"},
                      {"rect": RIGHT_DOOR, "sign": "FORTUNE TELLER", "to": "fortune"}],
            "people": [("lia", 470, 555, False)],
            "spots": [
                {"rect": (330, 392, 48, 46), "label": "Flower pot", "clue": "lockerkey"},
                {"rect": (690, 402, 44, 34), "label": "Bag on the steps", "clue": "chalk"},
                {"rect": (170, 200, 230, 200), "label": "Caravan with a red nose",
                 "look": ("Pip's Caravan", "A red nose is painted on the door. It's locked "
                          "and the curtains are closed.")},
                {"rect": (540, 210, 230, 190), "label": "Caravan with a light",
                 "look": ("Lia's Caravan", "Through the window you see a mat, weights and a "
                          "poster of Stella - with darts in it.")},
            ],
        },
    },
    "clues": {
        "cutrope": ("Cut Rope",
                    "The rope was cut almost through with a sharp blade - hours before the "
                    "show. Then it was rubbed with dust to hide the cut."),
        "greasepaint": ("White Face Paint",
                        "Greasy white smudges on the rope ladder up to the trapeze. Not "
                        "chalk - it's face paint, like clowns wear."),
        "ticket": ("VIP Ticket",
                   "Seat A1, front row. On the back, in pencil: 'Bonus when the show is "
                   "ruined. - G.'"),
        "knife": ("Igor's Knife",
                  "The strongman's knife, lying on the make-up table. Tiny rope fibres "
                  "stick to the blade."),
        "mirror": ("Writing on the Mirror",
                   "Pip's make-up mirror. Written in white face paint: 'A1 - after the "
                   "show - 5000'."),
        "locker": ("Envelope in Locker 7",
                   "Pip's locker: an envelope with 5,000 and a business card - 'Circus "
                   "Noir, C. Grey'."),
        "zorabook": ("Zora's Appointment Book",
                     "'18:30 - Pip. Asked if the trapeze will hold tonight. Strange "
                     "question for a clown.'"),
        "prediction": ("Zora's Poster",
                       "'Madame Zora predicts: tonight, a star will fall!'"),
        "lockerkey": ("Small Key",
                      "A small key marked '7', hidden in a flower pot next to the caravan "
                      "with the red nose."),
        "chalk": ("Chalk Bag",
                  "Lia's chalk bag, half empty. Acrobats use chalk for their hands."),
    },
    "culprit": "pip",
    "strong": ["greasepaint", "mirror", "locker", "zorabook"],
    "weak_text": {
        "cutrope": "The cut rope proves it was sabotage - not who did it.",
        "ticket": "The ticket points at Mr. Grey and a promise. But who actually climbed "
                  "up and cut the rope?",
        "knife": "The knife belongs to Igor. But whose hands were holding it?",
        "prediction": "A fortune teller's prediction is no proof in court.",
        "lockerkey": "A key alone proves nothing. What does it open?",
        "chalk": "Every acrobat uses chalk. This proves nothing.",
    },
    "confession": "Pip the clown confesses!",
    "solution": "Pip was going to lose his job after this season. Mr. Grey of Circus Noir "
                "offered him 5,000 and his own show if he ruined opening night. Pip asked "
                "Madame Zora if the trapeze would hold, borrowed Igor's knife at 17:00 and "
                "climbed the rope ladder - leaving white face paint on it - to cut the "
                "rope almost through. The money waited in his locker, and he wrote the "
                "deal on his mirror so he wouldn't forget it. (Mr. Grey will have to "
                "explain himself to the police, too.)",
    "suspects": {
        "krone": {
            "name": "Krone", "role": "Ringmaster", "style": "ringmaster", "accent": RED,
            "greeting": "Maximilian Krone, Ringmaster! The show must go on - but who wants "
                        "to destroy my show?",
            "topics": [
                {"q": "Is Stella insured?",
                 "a": "Of course! But without Stella there is no Circus Lumiere. I'd be "
                      "ruined, not rich."},
                {"q": "Who wants to hurt your circus?",
                 "a": "Mr. Grey of Circus Noir. He wants to buy us cheap. He sat in seat A1 "
                      "tonight, grinning like a shark."},
                {"q": "Is anyone leaving the circus?",
                 "a": "Pip. I told him last week that this is his last season. He took "
                      "it... badly."},
                {"q": "Is this Mr. Grey's ticket?", "req": "ticket",
                 "a": "Seat A1 - yes, I gave him that seat myself. 'Bonus when the show is "
                      "ruined'? That snake!"},
            ],
            "innocent": "Without Stella the ringmaster is ruined. He wanted to protect the "
                        "show, not destroy it. Krone is innocent.",
        },
        "pip": {
            "name": "Pip", "role": "Clown", "style": "clown", "accent": RED,
            "greeting": "Honk honk! Sorry, sorry. Not the moment for jokes, eh?",
            "topics": [
                {"q": "Where were you before the show?",
                 "a": "Making balloon animals for the kids! All afternoon. Ask anyone. Well, "
                      "ask the balloons."},
                {"q": "You borrowed Igor's knife.", "req": "knife",
                 "a": "For a balloon string! You can't cut balloon strings with your teeth, "
                      "can you?"},
                {"q": "Why is face paint on the ladder?", "req": "greasepaint",
                 "a": "Face paint? No, no. That's chalk! Lia's chalk! Yes."},
                {"q": "What does 'A1 - 5000' mean?", "req": "mirror",
                 "a": "It's... a phone number! Of my aunt! She lives in... A1."},
                {"q": "Why does Circus Noir pay you 5,000?", "req": "locker",
                 "a": "...They promised me my own show. Krone was going to fire me! I only "
                      "wanted Stella to miss one night!"},
            ],
            "innocent": "",
        },
        "lia": {
            "name": "Lia", "role": "Acrobat", "style": "acrobat", "accent": PINK,
            "greeting": "Before you ask: yes, I want Stella's spot. No, I would never cut a "
                        "rope. Ropes are sacred.",
            "topics": [
                {"q": "Where were you before the show?",
                 "a": "Training in my caravan from 17:00 to 19:30. Igor saw me through the "
                      "window - I stood on my hands for an hour."},
                {"q": "Who climbs the rope ladder?",
                 "a": "Only Stella, me and Igor. Nobody else would dare. Well, nobody "
                      "sane."},
                {"q": "Your chalk bag is half empty.", "req": "chalk",
                 "a": "Because I use it every day! Every acrobat does. Even Stella."},
                {"q": "What is on the rope ladder?", "req": "greasepaint",
                 "a": "That's not chalk - chalk is dusty. That's greasy white face paint. "
                      "Only one person here wears that."},
            ],
            "innocent": "Igor watched Lia train in her caravan the whole time the rope could "
                        "have been cut. Lia is innocent.",
        },
        "zora": {
            "name": "Madame Zora", "role": "Fortune Teller", "style": "fortune",
            "accent": PURPLE,
            "greeting": "I knew you would come, detective. The cards told me. Also, I saw "
                        "you walking over.",
            "topics": [
                {"q": "Who visited you today?",
                 "a": "Only one customer before the show. It's all in my appointment book."},
                {"q": "Can you see who did it?",
                 "a": "The crystal shows... a red nose. Or it's a reflection of the lamp. "
                      "The crystal is very old."},
                {"q": "You predicted a falling star!", "req": "prediction",
                 "a": "The cards showed THE TOWER - sudden disaster. And a clown asked me if "
                      "the trapeze would hold. I can add two and two."},
            ],
            "innocent": "Zora only repeated what a clown had asked her. Her 'prediction' was "
                        "good guessing. She is innocent.",
        },
        "igor": {
            "name": "Igor", "role": "Strongman", "style": "strongman", "accent": BLUE,
            "greeting": "Igor checks the ropes every morning. This morning: perfect! "
                        "Tonight: snap! Igor is very angry.",
            "topics": [
                {"q": "When did you check the rope?",
                 "a": "At 10:00. It was perfect. Somebody cut it after that."},
                {"q": "Who has the locker keys?",
                 "a": "Every artist has their own key. Pip always loses his. He hides it in "
                      "his flower pots."},
                {"q": "Did you see Lia before the show?",
                 "a": "Yes, through her window. On her hands, for an hour. Crazy woman."},
                {"q": "Is this your knife?", "req": "knife",
                 "a": "Yes. Pip borrowed it at 17:00 for a balloon. He brought it back at "
                      "19:00. Two hours for one balloon?"},
            ],
            "innocent": "Igor's knife was with Pip from 17:00 to 19:00 - exactly when the "
                        "rope was cut. Igor is innocent.",
        },
        "grey": {
            "name": "Mr. Grey", "role": "Owner, Circus Noir", "style": "rival",
            "accent": SILVER,
            "greeting": "Cornelius Grey, Circus Noir. I'm only a guest. A very... "
                        "interested guest.",
            "topics": [
                {"q": "Where were you before the show?",
                 "a": "Dinner in town, then seat A1 from 19:30. Lovely show. Shame about "
                      "the ending."},
                {"q": "Do you want to buy this circus?",
                 "a": "Every circus has its price. After tonight, Lumiere's price will be "
                      "much lower."},
                {"q": "'Bonus when the show is ruined'?", "req": "ticket",
                 "a": "My handwriting? Could be anybody's. I want my lawyer."},
                {"q": "Your card was in Pip's locker.", "req": "locker",
                 "a": "Pip? Never heard of him. ...Is he the one with the nose?"},
            ],
            "innocent": "Mr. Grey paid for the sabotage - but he never touched the rope. "
                        "You need the person who cut it. (The police will talk to Mr. Grey "
                        "later.)",
        },
    },
}


# ==========================================================================
# Look & feel of every case
#   scene      - picture behind the case intro (city, hotel, manor, train, carnival)
#   weather    - rain, snow or confetti
#   tint       - colour laid over every room (r, g, b, strength)
#   wall_style - plain, wainscot, wallpaper, brick, train, metal, tent, drape, night
#   floor      - tiles, wood, carpet, concrete, planks, sawdust, grass, stone
#   door       - wood, train or flap
#   enemy      - moving obstacle: polisher, trolley, dog, suitcase or ball
#   enemies    - how many of them are in every room
#   enemy_speed / enemy_mode - pixels per second, "patrol" (left-right) or "bounce"
# Rooms can override wall_style, floor and floor_color.
# ==========================================================================

CASE_1["theme"] = {"scene": "city", "weather": "rain", "tint": (20, 35, 70, 30),
                   "wall_style": "wainscot", "floor": "tiles",
                   "floor_color": (30, 31, 35), "door": "wood",
                   "enemy": "polisher", "enemy_name": "runaway floor polisher",
                   "enemies": 1, "enemy_speed": 90, "enemy_mode": "patrol"}
CASE_1["rooms"]["office"].update(wall_style="wallpaper", floor="wood",
                                 floor_color=(48, 36, 28))
CASE_1["rooms"]["storage"].update(wall_style="brick", floor="concrete",
                                  floor_color=(40, 40, 42))

CASE_2["theme"] = {"scene": "hotel", "weather": "rain", "tint": (80, 50, 10, 30),
                   "wall_style": "wallpaper", "floor": "carpet",
                   "floor_color": (74, 30, 34), "door": "wood",
                   "enemy": "trolley", "enemy_name": "rolling luggage trolleys",
                   "enemies": 2, "enemy_speed": 115, "enemy_mode": "patrol"}
CASE_2["rooms"]["kitchen"].update(wall_style="plain", floor="tiles",
                                  floor_color=(48, 50, 50))
CASE_2["rooms"]["fuseroom"].update(wall_style="brick", floor="concrete",
                                   floor_color=(36, 36, 38))

CASE_3["theme"] = {"scene": "manor", "weather": "rain", "tint": (50, 10, 20, 30),
                   "wall_style": "wainscot", "floor": "wood",
                   "floor_color": (50, 34, 24), "door": "wood", "lightning": True,
                   "enemy": "dog", "enemy_name": "professor's guard dogs",
                   "enemies": 2, "enemy_speed": 150, "enemy_mode": "patrol"}
CASE_3["rooms"]["dining"].update(wall_style="wallpaper")
CASE_3["rooms"]["lab"].update(wall_style="plain", floor="tiles",
                              floor_color=(40, 44, 48))
CASE_3["rooms"]["greenhouse"].update(wall_style="plain", floor="stone",
                                     floor_color=(44, 46, 42))

CASE_4["theme"] = {"scene": "train", "weather": "snow", "tint": (15, 30, 60, 25),
                   "wall_style": "train", "floor": "carpet",
                   "floor_color": (64, 24, 30), "door": "train",
                   "enemy": "suitcase", "enemy_name": "suitcases sliding around the shaking train",
                   "enemies": 3, "enemy_speed": 150, "enemy_mode": "bounce"}
CASE_4["rooms"]["luggage"].update(wall_style="metal", floor="planks",
                                  floor_color=(54, 44, 34))

CASE_5["theme"] = {"scene": "carnival", "weather": "confetti", "tint": (60, 10, 70, 28),
                   "wall_style": "tent", "floor": "sawdust",
                   "floor_color": (84, 68, 48), "door": "flap",
                   "enemy": "ball", "enemy_name": "bouncing circus balls",
                   "enemies": 4, "enemy_speed": 185, "enemy_mode": "bounce"}
CASE_5["rooms"]["backstage"].update(wall_style="wainscot", floor="planks",
                                    floor_color=(56, 44, 34))
CASE_5["rooms"]["fortune"].update(wall_style="drape", floor="carpet",
                                  floor_color=(50, 26, 50))
CASE_5["rooms"]["caravans"].update(wall_style="night", floor="grass",
                                   floor_color=(26, 36, 26))

# ==========================================================================
# Case files - the background story shown before every case (press F in game)
#   item_label / item / art / about - what was stolen (art = picture to draw)
#   client    - who asked the detective for help
#   timeline  - what we know about the evening
#   bios      - one line about every suspect
#   epilogue  - what happened after the case was solved
# ==========================================================================

CASE_1["story"] = {
    "item_label": "THE STOLEN ITEM", "item": "The Moonlit Night", "art": "painting",
    "about": "Painted in 1889 by Elias Varn, Greyhaven's most famous painter. It shows "
             "the harbour under a full moon. Varn finished it the night before he "
             "vanished at sea - it is his very last work. Every school child in "
             "Greyhaven has seen it. Value: about 2 million.",
    "client": "Greyhaven City Museum. Director Helga Weber called the police at 22:30.",
    "timeline": [("21:00", "Leon arrives to see the painting."),
                 ("21:30", "Leon leaves. Ole locks the front door."),
                 ("22:05", "Ole goes up to the roof after a phone call."),
                 ("22:10", "The security camera switches off."),
                 ("22:20", "The camera switches back on."),
                 ("22:25", "Ole finds the empty frame.")],
    "bios": {"karl": "Has cleaned the museum for 25 years. Knows every corner.",
             "weber": "Director for 6 years. Always elegant, always busy.",
             "leon": "A young painter. Can't stand the painter of the Moonlit Night.",
             "ole": "Night guard. Friendly, a bit nervous."},
    "epilogue": "The Moonlit Night was back on the wall the next morning. Ole got a pay "
                "rise - and Karl finally got a new mop.",
}

CASE_2["story"] = {
    "item_label": "THE STOLEN ITEM", "item": "The Ice Star", "art": "necklace",
    "about": "A necklace with 99 small diamonds and one big star-shaped diamond in the "
             "middle. It once belonged to a Russian princess, then to the Countess's "
             "grandmother. The Countess wears it only once a year - at her winter party "
             "in Hotel Aurora. 'Priceless', says the Countess. About 3 million, says "
             "everyone else.",
    "client": "Countess Valentina di Rocca, 78. She has spent every winter at the Aurora "
              "for 50 years.",
    "timeline": [("18:00", "Mia, the pianist, arrives at the hotel - very early."),
                 ("22:00", "The Countess's winter party begins."),
                 ("22:30", "The Ice Star is placed in a glass case for the guests."),
                 ("23:00", "Blackout! The whole hotel goes dark."),
                 ("23:05", "The lights come back. The glass case is empty.")],
    "bios": {"countess": "Rich, generous and a little dramatic.",
             "finch": "Runs the hotel. Worried about its good name.",
             "bruno": "The hotel chef. Loud, proud, flour everywhere.",
             "mia": "A young pianist. Plays every night in the ballroom."},
    "epilogue": "The Countess got her Ice Star back - and finally insured it. Bruno baked "
                "a new three-layer cake to celebrate.",
}

CASE_3["story"] = {
    "item_label": "THE STOLEN ITEM", "item": "The Ravenwood Formula", "art": "formula",
    "about": "Twelve pages of notes for a new battery - ten times stronger than any "
             "battery today. Professor Ravenwood worked on it for eleven years. With it, "
             "an electric car could drive across the whole country without stopping. "
             "Companies would pay millions for it.",
    "client": "Professor Ada Ravenwood, inventor. Brilliant, forgetful - and very angry "
              "right now.",
    "timeline": [("20:00", "Dinner begins. A thunderstorm starts outside."),
                 ("20:15", "Lily photographs the locked lab door."),
                 ("20:30", "Some guests leave the table for a short time."),
                 ("20:45", "The butler clears the table."),
                 ("21:00", "The professor goes to her lab. The safe is open - the "
                           "formula is gone.")],
    "bios": {"nora": "The professor's assistant for 3 years.",
             "felix": "The professor's nephew. Mostly interested in cake.",
             "hargreaves": "Butler for 30 years. Notices everything.",
             "lily": "Journalist. Here for the story of the year.",
             "victor": "Business partner. Owns half of the professor's company."},
    "epilogue": "The formula is safe again. The professor gave Nora a raise and a new "
                "hairpin. SolarCorp is now under investigation.",
}

CASE_4["story"] = {
    "item_label": "THE STOLEN ITEM", "item": "The Emperor's Egg", "art": "egg",
    "about": "A golden egg the size of an apple, covered in 300 rubies and emeralds. "
             "It was made in 1896 as an Easter present for an empress. When you open "
             "it, a tiny golden train rolls out. Now it travels to an exhibition in "
             "Venice - by train, of course. Value: about 5 million.",
    "client": "The Vienna Museum, which lent the egg to Venice. Its guard, Mr. Brandt, "
              "was supposed to protect it.",
    "timeline": [("19:00", "The Snowbound Express leaves Vienna."),
                 ("21:00", "Dinner in the dining car."),
                 ("22:30", "Snowstorm! The train stops high in the mountains."),
                 ("23:30", "The guard gets a hot chocolate."),
                 ("00:00", "Pavel finds the guard asleep and the cage empty.")],
    "bios": {"pavel": "Conductor for 20 years. Carries the only luggage car key.",
             "hassan": "A doctor on her way to a conference in Venice.",
             "teo": "Young waiter. His first winter on the Express.",
             "baron": "Rich art collector. Wanted to buy the egg.",
             "odile": "Famous opera singer. Travels with eleven suitcases."},
    "epilogue": "The snowplough arrived at dawn. The egg reached Venice just in time, "
                "and Teo got a medal for his honest answers.",
}

CASE_5["story"] = {
    "item_label": "WHAT WAS SABOTAGED", "item": "Stella's Golden Trapeze", "art": "trapeze",
    "about": "Stella's act is the highlight of Circus Lumiere: a triple somersault "
             "twelve metres above the ring. Tonight the trapeze rope snapped in the "
             "middle of her jump. Only the safety net saved her. Without Stella, the "
             "circus would have to close for good.",
    "client": "Stella Moreau, star acrobat. Unhurt but shaken - and determined to find "
              "out who did it.",
    "timeline": [("10:00", "Igor checks all ropes. Everything is fine."),
                 ("17:00", "The ring is empty while the artists get ready."),
                 ("19:30", "The show begins. Mr. Grey takes seat A1."),
                 ("21:40", "The rope snaps during Stella's jump.")],
    "bios": {"krone": "Owner and ringmaster. Loves his circus.",
             "pip": "The circus clown. Makes the children laugh.",
             "lia": "Acrobat. Always second behind Stella.",
             "zora": "Fortune teller. Says she can see the future.",
             "igor": "Strongman. Checks every rope and net.",
             "grey": "Owner of the rival Circus Noir. Visiting tonight."},
    "epilogue": "Circus Noir was closed down. In the next show Stella flew higher than "
                "ever, and the audience cheered louder than ever.",
}

CASES = [CASE_1, CASE_2, CASE_3, CASE_4, CASE_5]


# --------------------------------------------------------------------------
# Drawing helpers
# --------------------------------------------------------------------------

def load_font(size, bold=False, italic=False):
    for name in ("georgia", "timesnewroman", "times", "dejavuserif"):
        path = pygame.font.match_font(name, bold, italic)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size + 6)


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(color, amount):
    return tuple(max(0, min(255, c + amount)) for c in color[:3])


def wrap(text, font, width):
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split(" "):
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= width:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_text(s, msg, font, color, pos, center=False):
    img = font.render(msg, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    s.blit(img, rect)
    return rect


def draw_text_block(s, msg, font, color, x, y, width, gap=3):
    for line in wrap(msg, font, width):
        s.blit(font.render(line, True, color), (x, y))
        y += font.get_height() + gap
    return y


def glow(s, pos, radius, color, alpha):
    radius = int(radius)
    if radius < 2 or alpha <= 0:
        return
    g = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for i in range(6):
        r = int(radius * (1 - i / 6))
        pygame.draw.circle(g, (*color[:3], int(alpha * (i + 1) / 6)), (radius, radius), r)
    s.blit(g, (pos[0] - radius, pos[1] - radius))


def alpha_polygon(s, color, alpha, points):
    layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (*color[:3], alpha), points)
    s.blit(layer, (0, 0))


def alpha_ellipse(s, color, alpha, rect):
    r = pygame.Rect(rect)
    layer = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.ellipse(layer, (*color[:3], alpha), layer.get_rect())
    s.blit(layer, r.topleft)


def panel(s, rect, alpha=225, border=GOLD):
    rect = pygame.Rect(rect)
    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(layer, (10, 10, 14, alpha), layer.get_rect(), border_radius=8)
    s.blit(layer, rect.topleft)
    pygame.draw.rect(s, border, rect, 2, border_radius=8)


def shade_screen(s, alpha=170):
    layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    layer.fill((0, 0, 0, alpha))
    s.blit(layer, (0, 0))


def vertical_gradient(s, rect, top, bottom):
    r = pygame.Rect(rect)
    for y in range(r.h):
        pygame.draw.line(s, lerp_color(top, bottom, y / max(1, r.h - 1)),
                         (r.x, r.y + y), (r.right - 1, r.y + y))


def draw_star(s, center, filled, size=22):
    cx, cy = center
    points = []
    for k in range(10):
        r = size if k % 2 == 0 else size * 0.42
        a = -math.pi / 2 + k * math.pi / 5
        points.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pygame.draw.polygon(s, YELLOW if filled else GREY, points)


def draw_shadow(s, x, fy, width=90):
    alpha_ellipse(s, BLACK, 110, (x - width // 2, fy - 8, width, 18))


def draw_person(s, x, fy, style, accent, body=None, step=0.0):
    """Draws a figure standing with its feet at (x, fy). step makes the legs walk."""
    body = body or (16, 16, 20)
    rim = shade(body, 28)
    skin = (225, 225, 225) if style == "clown" else (62, 62, 68)
    hair = (26, 26, 30)
    wide = style in ("countess", "pianist", "singer", "fortune")
    big = style == "strongman"
    left_foot = x - 10 + int(step * 9)
    right_foot = x + 10 - int(step * 9)
    pygame.draw.line(s, body, (x - 10, fy - 60), (left_foot, fy - 4), 13)
    pygame.draw.line(s, body, (x + 10, fy - 60), (right_foot, fy - 4), 13)
    pygame.draw.ellipse(s, body, (left_foot - 12, fy - 6, 22, 10))
    pygame.draw.ellipse(s, body, (right_foot - 10, fy - 6, 22, 10))
    sh = 34 if big else 24
    if wide:
        torso = [(x - 42, fy), (x + 42, fy), (x + 24, fy - 132), (x - 24, fy - 132)]
    else:
        torso = [(x - 30, fy - 55), (x + 30, fy - 55), (x + sh, fy - 132), (x - sh, fy - 132)]
    pygame.draw.polygon(s, body, torso)
    arm_l = [(x - sh, fy - 130), (x - sh - 10, fy - 127), (x - sh - 16, fy - 70), (x - sh - 6, fy - 68)]
    arm_r = [(x + sh, fy - 130), (x + sh + 10, fy - 127), (x + sh + 16, fy - 70), (x + sh + 6, fy - 68)]
    pygame.draw.polygon(s, body, arm_l)
    pygame.draw.polygon(s, body, arm_r)
    # rim light on the right side makes the figures look less flat
    pygame.draw.line(s, rim, torso[1] if wide else (x + 30, fy - 55), torso[2], 2)
    pygame.draw.line(s, rim, arm_r[1], arm_r[2], 2)

    # hair / scarves behind the head
    if style in ("weber", "countess", "labcoat"):
        pygame.draw.circle(s, hair, (x, fy - 178), 9)
        pygame.draw.circle(s, hair, (x, fy - 158), 20)
    elif style in ("pianist", "acrobat"):
        pygame.draw.rect(s, hair, (x - 21, fy - 165, 42, 45), border_radius=8)
        pygame.draw.circle(s, hair, (x, fy - 158), 21)
    elif style == "journalist":
        pygame.draw.rect(s, hair, (x - 21, fy - 168, 42, 28), border_radius=8)
    elif style == "singer":
        for dx, dy in ((-16, -168), (0, -176), (16, -168), (-20, -150), (20, -150)):
            pygame.draw.circle(s, hair, (x + dx, fy + dy), 12)
    elif style == "doctor":
        pygame.draw.polygon(s, accent, [(x - 24, fy - 128), (x + 24, fy - 128), (x + 20, fy - 150),
                                        (x - 20, fy - 150)])
        pygame.draw.circle(s, accent, (x, fy - 157), 22)
    elif style == "fortune":
        pygame.draw.polygon(s, accent, [(x - 22, fy - 160), (x + 22, fy - 160), (x + 30, fy - 120),
                                        (x - 30, fy - 120)])
        pygame.draw.circle(s, accent, (x, fy - 160), 21)
    pygame.draw.rect(s, skin, (x - 6, fy - 142, 12, 12))
    head_r = 14 if style == "doctor" else 17
    pygame.draw.circle(s, skin, (x, fy - 155), head_r)
    eye = BLACK if style == "clown" else (120, 120, 128)
    pygame.draw.circle(s, eye, (x - 6, fy - 158), 2)
    pygame.draw.circle(s, eye, (x + 6, fy - 158), 2)

    if style == "detective":
        pygame.draw.polygon(s, body, [(x - 30, fy - 132), (x, fy - 112), (x + 30, fy - 132)])
        pygame.draw.ellipse(s, body, (x - 32, fy - 174, 64, 11))
        pygame.draw.rect(s, body, (x - 18, fy - 196, 36, 26), border_radius=6)
        pygame.draw.rect(s, (70, 30, 30), (x - 18, fy - 176, 36, 5))
    elif style == "karl":
        pygame.draw.rect(s, accent, (x - 20, fy - 112, 40, 58))
        pygame.draw.line(s, accent, (x - 16, fy - 112), (x - 12, fy - 130), 4)
        pygame.draw.line(s, accent, (x + 16, fy - 112), (x + 12, fy - 130), 4)
        pygame.draw.rect(s, shade(accent, -30), (x - 10, fy - 104, 20, 14))
        pygame.draw.ellipse(s, accent, (x - 18, fy - 178, 36, 18))
        pygame.draw.rect(s, accent, (x, fy - 168, 26, 5))
    elif style == "weber":
        pygame.draw.polygon(s, accent, [(x - 15, fy - 138), (x + 15, fy - 138),
                                        (x + 8, fy - 108), (x - 2, fy - 116)])
        pygame.draw.line(s, accent, (x - 5, fy - 146), (x + 5, fy - 146), 3)
    elif style == "leon":
        pygame.draw.ellipse(s, accent, (x - 22, fy - 180, 42, 15))
        pygame.draw.circle(s, accent, (x, fy - 181), 3)
        pygame.draw.rect(s, accent, (x - 16, fy - 137, 32, 8))
        pygame.draw.rect(s, accent, (x + 6, fy - 132, 9, 48))
    elif style == "ole":
        pygame.draw.rect(s, body, (x - 18, fy - 180, 36, 15), border_radius=4)
        pygame.draw.rect(s, body, (x - 22, fy - 168, 44, 5))
        pygame.draw.circle(s, accent, (x, fy - 173), 3)
        pygame.draw.circle(s, accent, (x - 13, fy - 112), 5)
    elif style == "countess":
        pygame.draw.polygon(s, accent, [(x - 10, fy - 172), (x - 5, fy - 184), (x, fy - 174),
                                        (x + 5, fy - 184), (x + 10, fy - 172)])
        pygame.draw.arc(s, accent, (x - 30, fy - 150, 60, 50), math.pi, 2 * math.pi, 6)
        pygame.draw.line(s, (90, 90, 96), (x - 9, fy - 132), (x + 9, fy - 132), 2)
    elif style == "manager":
        pygame.draw.arc(s, hair, (x - 18, fy - 174, 36, 30), 0, math.pi, 7)
        pygame.draw.polygon(s, WHITE, [(x - 9, fy - 132), (x + 9, fy - 132), (x, fy - 112)])
        pygame.draw.polygon(s, accent, [(x - 10, fy - 134), (x, fy - 129), (x - 10, fy - 124)])
        pygame.draw.polygon(s, accent, [(x + 10, fy - 134), (x, fy - 129), (x + 10, fy - 124)])
    elif style == "chef":
        pygame.draw.rect(s, (210, 210, 210), (x - 15, fy - 196, 30, 26))
        for cx in (x - 10, x, x + 10):
            pygame.draw.circle(s, (210, 210, 210), (cx, fy - 196), 9)
        pygame.draw.rect(s, (190, 190, 190), (x - 20, fy - 115, 40, 75))
        pygame.draw.polygon(s, accent, [(x - 12, fy - 136), (x + 12, fy - 136), (x, fy - 122)])
    elif style == "pianist":
        pygame.draw.rect(s, accent, (x - 22, fy - 172, 12, 6))
        pygame.draw.circle(s, accent, (x, fy - 118), 5)
    elif style == "labcoat":
        pygame.draw.polygon(s, (200, 200, 200), [(x - 32, fy - 40), (x - 4, fy - 40),
                                                 (x - 4, fy - 128), (x - 24, fy - 132)])
        pygame.draw.polygon(s, (200, 200, 200), [(x + 32, fy - 40), (x + 4, fy - 40),
                                                 (x + 4, fy - 128), (x + 24, fy - 132)])
        pygame.draw.circle(s, accent, (x - 7, fy - 157), 6, 2)
        pygame.draw.circle(s, accent, (x + 7, fy - 157), 6, 2)
    elif style == "nephew":
        for hx in range(x - 16, x + 17, 8):
            pygame.draw.circle(s, hair, (hx, fy - 170), 7)
        for y in (fy - 120, fy - 100, fy - 80):
            pygame.draw.line(s, accent, (x - 26, y), (x + 26, y), 4)
    elif style == "butler":
        pygame.draw.polygon(s, WHITE, [(x - 10, fy - 132), (x + 10, fy - 132), (x, fy - 100)])
        pygame.draw.polygon(s, body, [(x - 9, fy - 133), (x, fy - 128), (x - 9, fy - 123)])
        pygame.draw.polygon(s, body, [(x + 9, fy - 133), (x, fy - 128), (x + 9, fy - 123)])
        pygame.draw.arc(s, (110, 110, 116), (x - 10, fy - 170, 14, 10), 0.5, 2.5, 2)
        pygame.draw.ellipse(s, accent, (x + 30, fy - 100, 50, 10))
    elif style == "journalist":
        pygame.draw.line(s, accent, (x - 20, fy - 132), (x + 4, fy - 100), 2)
        pygame.draw.rect(s, accent, (x - 6, fy - 108, 24, 16), border_radius=3)
        pygame.draw.circle(s, body, (x + 6, fy - 100), 5)
    elif style == "partner":
        pygame.draw.rect(s, body, (x - 15, fy - 210, 30, 38))
        pygame.draw.rect(s, body, (x - 24, fy - 175, 48, 6))
        pygame.draw.rect(s, (150, 40, 40), (x - 15, fy - 182, 30, 5))
        pygame.draw.line(s, hair, (x - 8, fy - 147), (x + 8, fy - 147), 3)
        pygame.draw.line(s, (120, 90, 60), (x + 6, fy - 143), (x + 24, fy - 140), 3)
        pygame.draw.circle(s, accent, (x + 25, fy - 140), 3)
    elif style == "conductor":
        pygame.draw.rect(s, body, (x - 18, fy - 182, 36, 16), border_radius=3)
        pygame.draw.rect(s, body, (x - 4, fy - 170, 26, 5))
        pygame.draw.circle(s, accent, (x, fy - 175), 4)
        for row in range(4):
            pygame.draw.circle(s, accent, (x - 8, fy - 120 + row * 16), 3)
            pygame.draw.circle(s, accent, (x + 8, fy - 120 + row * 16), 3)
        pygame.draw.line(s, accent, (x + 8, fy - 70), (x + 26, fy - 58), 2)
    elif style == "singer":
        pygame.draw.arc(s, accent, (x - 34, fy - 148, 68, 52), math.pi, 2 * math.pi, 7)
        for k in range(7):
            a = math.pi + k * math.pi / 6
            pygame.draw.circle(s, accent, (int(x + 34 * math.cos(a)), int(fy - 122 - 26 * math.sin(a))), 5)
        pygame.draw.circle(s, accent, (x - 15, fy - 146), 3)
        pygame.draw.circle(s, accent, (x + 15, fy - 146), 3)
        pygame.draw.line(s, RED, (x - 5, fy - 147), (x + 5, fy - 147), 3)
    elif style == "baron":
        pygame.draw.line(s, accent, (x - 22, fy - 128), (x + 24, fy - 62), 6)
        pygame.draw.circle(s, accent, (x + 6, fy - 158), 6, 2)
        pygame.draw.line(s, accent, (x + 12, fy - 156), (x + 18, fy - 130), 1)
        pygame.draw.arc(s, hair, (x - 16, fy - 152, 16, 10), 0, math.pi, 3)
        pygame.draw.arc(s, hair, (x, fy - 152, 16, 10), 0, math.pi, 3)
        pygame.draw.circle(s, accent, (x - 12, fy - 112), 5)
    elif style == "doctor":
        pygame.draw.arc(s, (190, 190, 200), (x - 16, fy - 140, 32, 40), math.pi, 2 * math.pi, 2)
        pygame.draw.line(s, (190, 190, 200), (x + 16, fy - 120), (x + 14, fy - 92), 2)
        pygame.draw.circle(s, (190, 190, 200), (x + 14, fy - 88), 5)
    elif style == "waiter":
        pygame.draw.polygon(s, (205, 205, 205), [(x - 30, fy - 70), (x + 30, fy - 70),
                                                 (x + 24, fy - 132), (x - 24, fy - 132)])
        pygame.draw.polygon(s, body, [(x - 9, fy - 134), (x, fy - 129), (x - 9, fy - 124)])
        pygame.draw.polygon(s, body, [(x + 9, fy - 134), (x, fy - 129), (x + 9, fy - 124)])
        pygame.draw.ellipse(s, accent, (x + 28, fy - 104, 46, 9))
        pygame.draw.rect(s, (200, 220, 230), (x + 46, fy - 120, 8, 16))
        pygame.draw.arc(s, hair, (x - 18, fy - 174, 36, 26), 0, math.pi, 6)
    elif style == "ringmaster":
        pygame.draw.polygon(s, (120, 28, 34), [(x - 30, fy - 55), (x - 4, fy - 55),
                                               (x - 4, fy - 130), (x - 24, fy - 132)])
        pygame.draw.polygon(s, (120, 28, 34), [(x + 30, fy - 55), (x + 4, fy - 55),
                                               (x + 4, fy - 130), (x + 24, fy - 132)])
        for row in range(3):
            pygame.draw.circle(s, GOLD, (x - 10, fy - 118 + row * 18), 3)
        pygame.draw.rect(s, body, (x - 16, fy - 214, 32, 42))
        pygame.draw.rect(s, body, (x - 26, fy - 176, 52, 6))
        pygame.draw.rect(s, accent, (x - 16, fy - 186, 32, 6))
        pygame.draw.arc(s, hair, (x - 18, fy - 152, 18, 12), 0, math.pi, 3)
        pygame.draw.arc(s, hair, (x, fy - 152, 18, 12), 0, math.pi, 3)
    elif style == "clown":
        for dx in (-22, -16, 16, 22):
            pygame.draw.circle(s, ORANGE, (x + dx, fy - 162 + abs(dx) // 3), 8)
        pygame.draw.circle(s, accent, (x, fy - 151), 6)
        pygame.draw.arc(s, accent, (x - 9, fy - 152, 18, 12), math.pi + 0.3, 2 * math.pi - 0.3, 2)
        for k in range(6):
            pygame.draw.circle(s, WHITE, (x - 20 + k * 8, fy - 134), 6)
        for px, py in ((x - 12, fy - 112), (x + 10, fy - 96), (x - 6, fy - 78), (x + 14, fy - 66)):
            pygame.draw.circle(s, accent, (px, py), 5)
    elif style == "acrobat":
        pygame.draw.polygon(s, accent, [(x - 22, fy - 55), (x + 22, fy - 55),
                                        (x + 22, fy - 128), (x - 22, fy - 128)])
        pygame.draw.line(s, WHITE, (x - 20, fy - 120), (x + 20, fy - 70), 2)
        pygame.draw.circle(s, hair, (x + 18, fy - 168), 8)
        pygame.draw.line(s, hair, (x + 22, fy - 166), (x + 30, fy - 140), 6)
    elif style == "fortune":
        for k in range(5):
            pygame.draw.circle(s, GOLD, (x - 16 + k * 8, fy - 170), 3)
        pygame.draw.circle(s, GOLD, (x - 17, fy - 142), 7, 2)
        pygame.draw.circle(s, GOLD, (x + 17, fy - 142), 7, 2)
        pygame.draw.polygon(s, shade(accent, -40), [(x - 32, fy - 128), (x + 32, fy - 128), (x, fy - 80)])
    elif style == "strongman":
        for y in range(int(fy - 126), int(fy - 56), 10):
            pygame.draw.line(s, accent, (x - 28, y), (x + 28, y), 4)
        pygame.draw.arc(s, hair, (x - 22, fy - 152, 22, 16), 0, math.pi, 4)
        pygame.draw.arc(s, hair, (x, fy - 152, 22, 16), 0, math.pi, 4)
        pygame.draw.circle(s, (80, 80, 86), (x - 4, fy - 166), 4)
    elif style == "rival":
        pygame.draw.polygon(s, (54, 56, 62), [(x - 30, fy - 55), (x + 30, fy - 55),
                                              (x + 24, fy - 132), (x - 24, fy - 132)])
        pygame.draw.polygon(s, WHITE, [(x - 8, fy - 132), (x + 8, fy - 132), (x, fy - 108)])
        pygame.draw.line(s, (30, 30, 34), (x, fy - 130), (x, fy - 104), 3)
        pygame.draw.circle(s, accent, (x + 2, fy - 118), 2)
        pygame.draw.ellipse(s, body, (x - 22, fy - 176, 44, 10))
        pygame.draw.ellipse(s, body, (x - 15, fy - 192, 30, 24))
        pygame.draw.line(s, (90, 70, 50), (x + 44, fy - 70), (x + 52, fy), 3)


def draw_tick(s, pos):
    x, y = pos
    pygame.draw.circle(s, BLACK, pos, 11)
    pygame.draw.circle(s, GOLD, pos, 11, 2)
    pygame.draw.lines(s, GOLD, False, [(x - 5, y), (x - 1, y + 4), (x + 6, y - 5)], 3)


def draw_crate(s, rect):
    x, y, w, h = rect
    pygame.draw.rect(s, WOOD, rect)
    for k in range(1, 4):
        pygame.draw.line(s, shade(WOOD, -10), (x, y + k * h // 4), (x + w, y + k * h // 4), 1)
    pygame.draw.rect(s, WOOD_DARK, rect, 4)
    pygame.draw.line(s, WOOD_DARK, (x, y), (x + w, y + h), 4)
    pygame.draw.line(s, shade(WOOD, 18), (x + 4, y + 4), (x + w - 4, y + 4), 1)


def draw_suitcase(s, rect, color):
    r = pygame.Rect(rect)
    pygame.draw.rect(s, color, r, border_radius=6)
    pygame.draw.rect(s, shade(color, -25), r, 2, border_radius=6)
    pygame.draw.rect(s, shade(color, -25), (r.centerx - 12, r.y - 8, 24, 10), 3, border_radius=3)
    for bx in (r.x + 12, r.right - 18):
        pygame.draw.rect(s, BRASS, (bx, r.y + 4, 6, 8))
    pygame.draw.line(s, shade(color, 20), (r.x + 6, r.y + 3), (r.right - 6, r.y + 3), 1)


def draw_chandelier(s, x, y, lit=True):
    pygame.draw.line(s, BLACK, (x, TOP_BAR), (x, y), 2)
    pygame.draw.arc(s, (120, 110, 80), (x - 50, y - 10, 100, 30), math.pi, 2 * math.pi, 3)
    for dx in (-45, -22, 0, 22, 45):
        cy = y + 5 - abs(dx) // 10
        pygame.draw.rect(s, (200, 200, 200), (x + dx - 2, cy - 10, 4, 10))
        pygame.draw.line(s, (170, 190, 200), (x + dx, cy + 2), (x + dx, cy + 12), 1)
        if lit:
            pygame.draw.circle(s, YELLOW, (x + dx, cy - 13), 3)
    if lit:
        glow(s, (x, y), 80, YELLOW, 70)


def draw_wall_lamp(s, x, y, color=YELLOW):
    pygame.draw.rect(s, BRASS, (x - 3, y, 6, 18))
    pygame.draw.polygon(s, (220, 200, 160), [(x - 12, y - 6), (x + 12, y - 6), (x + 8, y - 22), (x - 8, y - 22)])
    glow(s, (x, y - 10), 45, color, 70)


def draw_shelf_of_books(s, rect, seed):
    x, y, w, h = rect
    pygame.draw.rect(s, WOOD_DARK, rect)
    rng = random.Random(seed)
    for row in range(5):
        by = y + 12 + row * (h - 20) // 5
        bx = x + 8
        while bx < x + w - 14:
            bw = rng.randint(8, 16)
            bh = rng.randint(35, 50)
            tone = rng.randint(55, 105)
            book = (tone, tone - 6, tone - 10)
            pygame.draw.rect(s, book, (bx, by + 52 - bh, bw, bh))
            pygame.draw.line(s, shade(book, 25), (bx + 2, by + 56 - bh), (bx + bw - 3, by + 56 - bh), 1)
            bx += bw + 2
        pygame.draw.rect(s, WOOD, (x, by + 52, w, 8))
    pygame.draw.rect(s, WOOD, rect, 6)


def draw_string_lights(s, start, end, sag, t, count=14):
    (x1, y1), (x2, y2) = start, end
    points = []
    for i in range(41):
        f = i / 40
        points.append((x1 + (x2 - x1) * f, y1 + (y2 - y1) * f + sag * 4 * f * (1 - f)))
    pygame.draw.lines(s, (30, 30, 34), False, points, 2)
    for i in range(1, count):
        f = i / count
        bx = x1 + (x2 - x1) * f
        by = y1 + (y2 - y1) * f + sag * 4 * f * (1 - f) + 5
        color = BULB_COLORS[(i + int(t * 2)) % len(BULB_COLORS)]
        pygame.draw.circle(s, color, (int(bx), int(by)), 4)
        glow(s, (bx, by), 14, color, 60)


# --------------------------------------------------------------------------
# Moving obstacles - every case has its own kind
# --------------------------------------------------------------------------

def draw_enemy(s, kind, x, y, t, vx):
    x, y = int(x), int(y)
    facing = 1 if vx >= 0 else -1
    draw_shadow(s, x, y, 70)
    if kind == "polisher":
        pygame.draw.line(s, (90, 92, 98), (x - 10 * facing, y - 26), (x - 34 * facing, y - 80), 4)
        pygame.draw.line(s, (40, 40, 44), (x - 42 * facing, y - 84), (x - 26 * facing, y - 76), 7)
        pygame.draw.ellipse(s, (120, 124, 132), (x - 32, y - 30, 64, 26))
        pygame.draw.ellipse(s, (160, 164, 172), (x - 22, y - 36, 44, 16))
        pygame.draw.ellipse(s, (40, 40, 44), (x - 34, y - 10, 68, 12))
        for k in range(6):
            a = t * 14 + k
            pygame.draw.line(s, (200, 200, 200), (x, y - 4), (x + 30 * math.cos(a), y - 4 + 5 * math.sin(a)), 1)
        pygame.draw.circle(s, RED if int(t * 6) % 2 else (90, 20, 20), (x + 14 * facing, y - 30), 4)
    elif kind == "trolley":
        pygame.draw.rect(s, BRASS, (x - 40, y - 18, 80, 8))
        pygame.draw.line(s, BRASS, (x - 34, y - 18), (x - 34, y - 110), 4)
        pygame.draw.line(s, BRASS, (x + 34, y - 18), (x + 34, y - 110), 4)
        pygame.draw.arc(s, BRASS, (x - 34, y - 140, 68, 60), 0, math.pi, 4)
        draw_suitcase(s, (x - 30, y - 50, 60, 32), (120, 40, 50))
        draw_suitcase(s, (x - 24, y - 84, 48, 28), (60, 80, 120))
        for wx in (x - 32, x + 32):
            pygame.draw.circle(s, BLACK, (wx, y - 4), 7)
            pygame.draw.circle(s, GREY, (wx, y - 4), 3)
    elif kind == "dog":
        run = math.sin(t * 16)
        body = (14, 14, 16)
        pygame.draw.ellipse(s, body, (x - 34, y - 46, 68, 28))
        for lx, ph in ((x - 22, run), (x - 10, -run), (x + 12, run), (x + 24, -run)):
            pygame.draw.line(s, body, (lx, y - 24), (lx + int(ph * 7), y - 2), 6)
        hx = x + 34 * facing
        pygame.draw.circle(s, body, (hx, y - 52), 14)
        pygame.draw.polygon(s, body, [(hx + 8 * facing, y - 54), (hx + 26 * facing, y - 48), (hx + 8 * facing, y - 42)])
        pygame.draw.polygon(s, body, [(hx - 8, y - 62), (hx - 2, y - 78), (hx + 4, y - 62)])
        pygame.draw.circle(s, RED, (hx + 6 * facing, y - 56), 3)
        glow(s, (hx + 6 * facing, y - 56), 10, RED, 120)
        pygame.draw.line(s, body, (x - 34 * facing, y - 40), (x - 50 * facing, y - 54 + int(run * 6)), 5)
    elif kind == "suitcase":
        tilt = math.sin(t * 6) * 8
        case = pygame.Surface((70, 50), pygame.SRCALPHA)
        draw_suitcase(case, (5, 12, 60, 36), (110, 70, 40))
        case = pygame.transform.rotate(case, tilt)
        s.blit(case, case.get_rect(midbottom=(x, y + 2)))
        for k in range(3):
            pygame.draw.line(s, (200, 206, 218), (x - 40 * facing - k * 6 * facing, y - 12 - k * 10),
                             (x - 56 * facing - k * 6 * facing, y - 12 - k * 10), 2)
    elif kind == "ball":
        hop = abs(math.sin(t * 5)) * 40
        cy = int(y - 24 - hop)
        pygame.draw.circle(s, (230, 216, 196), (x, cy), 24)
        for k, color in enumerate(((200, 40, 55), (60, 100, 200), (240, 200, 60))):
            a = t * 4 * facing + k * 2.1
            pygame.draw.polygon(s, color, [(x, cy), (x + 24 * math.cos(a), cy + 24 * math.sin(a)),
                                           (x + 24 * math.cos(a + 0.9), cy + 24 * math.sin(a + 0.9))])
        pygame.draw.circle(s, (40, 20, 30), (x, cy), 24, 2)
        pygame.draw.circle(s, WHITE, (x - 8, cy - 9), 4)



# --------------------------------------------------------------------------
# Intro scenes - one big picture per case
# --------------------------------------------------------------------------

def scene_city(s, fonts):
    vertical_gradient(s, (0, 0, WIDTH, HEIGHT), (12, 13, 18), (52, 56, 66))
    pygame.draw.circle(s, (190, 193, 200), (55, 110), 28)
    pygame.draw.ellipse(s, (34, 37, 44), (10, 118, 110, 18))
    for rect in ((0, 200, 110, 300), (100, 240, 90, 260), (770, 210, 100, 290), (860, 170, 100, 330)):
        pygame.draw.rect(s, (38, 41, 48), rect)
    pygame.draw.polygon(s, (48, 52, 60), [(330, 250), (480, 190), (630, 250)])
    pygame.draw.rect(s, (53, 57, 66), (330, 250, 300, 24))
    for i in range(6):
        pygame.draw.rect(s, (60, 65, 75), (345 + i * 52, 274, 18, 160))
        pygame.draw.line(s, (72, 78, 90), (349 + i * 52, 274), (349 + i * 52, 434), 2)
    pygame.draw.rect(s, (53, 57, 66), (322, 434, 316, 14))
    draw_text(s, "M U S E U M", fonts[0], (130, 135, 145), (480, 234), center=True)
    pygame.draw.rect(s, YELLOW, (470, 330, 16, 26))
    pygame.draw.rect(s, (20, 22, 27), (0, 290, 240, 190))
    pygame.draw.polygon(s, (20, 22, 27), [(0, 290), (120, 245), (240, 290)])
    pygame.draw.rect(s, (20, 22, 27), (700, 300, 260, 180))
    for x, y, lit in ((30, 320, 1), (80, 320, 0), (180, 320, 1), (30, 390, 0),
                      (180, 390, 0), (730, 330, 0), (790, 330, 1), (850, 330, 0), (730, 400, 1)):
        pygame.draw.rect(s, YELLOW if lit else (45, 45, 40), (x, y, 24, 32))
        pygame.draw.line(s, (20, 22, 27), (x + 12, y), (x + 12, y + 32), 2)
    pygame.draw.rect(s, (28, 30, 36), (840, 400, 80, 26))
    pygame.draw.rect(s, GREY, (840, 400, 80, 26), 1)
    draw_text(s, "BAR", fonts[0], LIGHT_GREY, (880, 413), center=True)
    pygame.draw.rect(s, (27, 30, 36), (0, 470, WIDTH, 130))
    pygame.draw.rect(s, (42, 46, 54), (0, 470, WIDTH, 16))
    for x in range(0, WIDTH, 70):
        pygame.draw.rect(s, (55, 60, 70), (x, 545, 40, 4))
    alpha_polygon(s, YELLOW, 45, [(648, 170), (672, 170), (790, 486), (530, 486)])
    pygame.draw.rect(s, BLACK, (656, 170, 8, 316))
    pygame.draw.polygon(s, BLACK, [(636, 168), (684, 168), (674, 148), (646, 148)])
    pygame.draw.rect(s, YELLOW, (644, 166, 32, 7))
    glow(s, (660, 170), 80, YELLOW, 120)
    pygame.draw.ellipse(s, (55, 62, 76), (220, 495, 200, 28))
    draw_person(s, 320, 500, "detective", RED, body=PLAYER_PURPLE)
    for i, (x, y) in enumerate(((410, 492), (428, 484), (440, 476), (455, 468), (463, 460))):
        pygame.draw.ellipse(s, RED, (x - 6 + i, y, 12 - i, 6 - i // 2))
    glow(s, (425, 486), 30, RED, 90)


def scene_hotel(s, fonts):
    vertical_gradient(s, (0, 0, WIDTH, HEIGHT), (22, 14, 30), (74, 46, 52))
    rng = random.Random(4)
    for x in range(0, WIDTH, 90):
        h = rng.randint(180, 320)
        pygame.draw.rect(s, (36, 28, 38), (x, 470 - h, 86, h))
        for wy in range(470 - h + 15, 450, 28):
            for wx in range(x + 10, x + 80, 22):
                if rng.random() < 0.3:
                    pygame.draw.rect(s, (120, 90, 60), (wx, wy, 10, 14))
    # hotel facade
    pygame.draw.rect(s, (66, 52, 48), (270, 130, 420, 350))
    pygame.draw.rect(s, (86, 70, 62), (260, 120, 440, 14))
    for row in range(6):
        for col in range(7):
            wx, wy = 292 + col * 56, 150 + row * 46
            lit = rng.random() < 0.6
            pygame.draw.rect(s, (255, 205, 120) if lit else (40, 34, 36), (wx, wy, 30, 30))
            pygame.draw.line(s, (66, 52, 48), (wx + 15, wy), (wx + 15, wy + 30), 2)
            pygame.draw.rect(s, (96, 80, 70), (wx - 4, wy + 30, 38, 4))
    # neon sign
    pygame.draw.rect(s, (20, 14, 20), (330, 64, 300, 52), border_radius=6)
    for r in (120, 80):
        glow(s, (480, 90), r, (255, 80, 150), 40)
    draw_text(s, "HOTEL AURORA", fonts[1], (255, 120, 180), (480, 90), center=True)
    # entrance with awning and revolving door
    pygame.draw.rect(s, (255, 205, 120), (440, 400, 80, 70))
    pygame.draw.line(s, (90, 70, 50), (480, 400), (480, 470), 3)
    pygame.draw.polygon(s, (120, 30, 40), [(400, 384), (560, 384), (585, 410), (375, 410)])
    for k in range(8):
        pygame.draw.line(s, (160, 50, 60), (385 + k * 26, 410), (405 + k * 20, 384), 2)
    # street with reflections
    pygame.draw.rect(s, (24, 20, 28), (0, 470, WIDTH, 130))
    pygame.draw.rect(s, (46, 38, 44), (0, 470, WIDTH, 14))
    for x, c in ((480, (255, 80, 150)), (330, (255, 205, 120)), (620, (255, 205, 120))):
        alpha_polygon(s, c, 45, [(x - 30, 486), (x + 30, 486), (x + 12, 600), (x - 12, 600)])
    # car
    pygame.draw.polygon(s, (14, 14, 16), [(600, 470), (610, 440), (660, 425), (760, 425),
                                          (800, 445), (840, 450), (845, 470)])
    for wx in (640, 800):
        pygame.draw.circle(s, BLACK, (wx, 472), 16)
        pygame.draw.circle(s, (60, 60, 66), (wx, 472), 7)
    pygame.draw.circle(s, YELLOW, (842, 456), 5)
    glow(s, (842, 456), 30, YELLOW, 90)
    draw_shadow(s, 190, 500)
    draw_person(s, 190, 500, "detective", RED, body=PLAYER_PURPLE)


def scene_manor(s, fonts):
    vertical_gradient(s, (0, 0, WIDTH, HEIGHT), (10, 14, 16), (44, 50, 52))
    for cx, cy, w in ((150, 90, 300), (520, 60, 380), (820, 120, 260)):
        pygame.draw.ellipse(s, (30, 34, 38), (cx - w // 2, cy - 30, w, 70))
    bolt = [(760, 40), (740, 120), (770, 120), (735, 230), (800, 105), (770, 105), (795, 40)]
    glow(s, (770, 130), 120, (180, 200, 255), 50)
    pygame.draw.polygon(s, (220, 230, 255), bolt)
    pygame.draw.polygon(s, (16, 20, 18), [(0, 420), (200, 360), (480, 330), (760, 350), (960, 400),
                                          (960, 600), (0, 600)])
    # mansion
    dark = (24, 26, 28)
    pygame.draw.rect(s, dark, (300, 210, 360, 150))
    for tx in (290, 620):
        pygame.draw.rect(s, dark, (tx, 160, 50, 200))
        pygame.draw.polygon(s, dark, [(tx - 8, 160), (tx + 25, 100), (tx + 58, 160)])
    pygame.draw.polygon(s, dark, [(330, 210), (480, 150), (630, 210)])
    pygame.draw.rect(s, dark, (520, 150, 16, 40))
    rng = random.Random(9)
    for row in range(3):
        for col in range(8):
            wx, wy = 318 + col * 42, 226 + row * 40
            lit = rng.random() < 0.25
            pygame.draw.rect(s, YELLOW if lit else (40, 44, 46), (wx, wy, 18, 24))
            if lit:
                glow(s, (wx + 9, wy + 12), 20, YELLOW, 60)
    pygame.draw.rect(s, (60, 44, 30), (462, 316, 36, 44))
    # dead tree
    def branch(x, y, angle, length, width):
        if length < 8:
            return
        x2 = x + length * math.cos(angle)
        y2 = y - length * math.sin(angle)
        pygame.draw.line(s, (14, 16, 14), (x, y), (x2, y2), width)
        branch(x2, y2, angle + 0.45, length * 0.7, max(1, width - 2))
        branch(x2, y2, angle - 0.35, length * 0.68, max(1, width - 2))
    branch(140, 420, math.pi / 2, 90, 10)
    # iron fence
    for x in range(0, WIDTH, 18):
        if 420 < x < 540:
            continue
        pygame.draw.line(s, (10, 10, 12), (x, 470), (x, 560), 4)
        pygame.draw.polygon(s, (10, 10, 12), [(x - 5, 472), (x, 458), (x + 5, 472)])
    pygame.draw.rect(s, (10, 10, 12), (0, 490, 420, 5))
    pygame.draw.rect(s, (10, 10, 12), (540, 490, 420, 5))
    draw_shadow(s, 480, 575)
    draw_person(s, 480, 575, "detective", RED, body=PLAYER_PURPLE)


def scene_train(s, fonts):
    vertical_gradient(s, (0, 0, WIDTH, 440), (8, 12, 30), (46, 60, 96))
    rng = random.Random(3)
    for _ in range(90):
        pygame.draw.circle(s, (220, 225, 240), (rng.randint(0, WIDTH), rng.randint(0, 260)), 1)
    glow(s, (790, 100), 110, (200, 210, 255), 60)
    pygame.draw.circle(s, (230, 232, 240), (790, 100), 40)
    pygame.draw.circle(s, (200, 204, 216), (775, 92), 8)
    for color, base, peaks in (((48, 58, 86), 330, [(0, 300), (140, 170), (260, 280), (420, 150),
                                                    (600, 290), (760, 180), (960, 300)]),
                               ((34, 42, 64), 380, [(0, 350), (180, 230), (330, 340), (520, 220),
                                                    (700, 340), (880, 240), (960, 300)])):
        pygame.draw.polygon(s, color, peaks + [(960, 440), (0, 440)])
        for px, py in peaks[1:-1]:
            if py < 300:
                pygame.draw.polygon(s, (215, 220, 232), [(px, py), (px - 28, py + 30), (px - 8, py + 22),
                                                         (px + 6, py + 32), (px + 26, py + 30)])
    pygame.draw.rect(s, (200, 206, 218), (0, 430, WIDTH, 170))
    vertical_gradient(s, (0, 470, WIDTH, 130), (200, 206, 218), (150, 158, 176))
    pygame.draw.rect(s, (60, 56, 52), (0, 452, WIDTH, 6))
    for x in range(0, WIDTH, 26):
        pygame.draw.rect(s, (90, 80, 70), (x, 456, 14, 6))
    # train cars with warm windows
    for cx in (40, 230, 420):
        pygame.draw.rect(s, (40, 26, 24), (cx, 350, 180, 90), border_radius=6)
        pygame.draw.rect(s, (60, 36, 32), (cx, 344, 180, 10), border_radius=4)
        pygame.draw.rect(s, (220, 225, 235), (cx + 4, 340, 172, 5))
        for wx in range(cx + 14, cx + 170, 32):
            pygame.draw.rect(s, (255, 205, 120), (wx, 368, 20, 26))
            glow(s, (wx + 10, 381), 24, (255, 205, 120), 50)
        pygame.draw.line(s, GOLD, (cx, 410), (cx + 180, 410), 2)
        for wx in (cx + 30, cx + 150):
            pygame.draw.circle(s, BLACK, (wx, 444), 12)
    # locomotive
    pygame.draw.rect(s, (22, 22, 26), (610, 330, 130, 110))
    pygame.draw.rect(s, (22, 22, 26), (730, 360, 110, 80), border_radius=20)
    pygame.draw.rect(s, (22, 22, 26), (780, 320, 26, 44))
    pygame.draw.rect(s, (255, 205, 120), (630, 350, 34, 30))
    for k in range(5):
        glow(s, (795 - k * 30, 300 - k * 45), 30 + k * 10, (160, 165, 180), 60)
    pygame.draw.circle(s, YELLOW, (842, 395), 8)
    alpha_polygon(s, YELLOW, 50, [(842, 388), (960, 340), (960, 470), (842, 402)])
    for wx in (650, 700, 760, 810):
        pygame.draw.circle(s, BLACK, (wx, 442), 15)
        pygame.draw.circle(s, (70, 70, 76), (wx, 442), 5)
    # pine trees
    for tx, ty, h in ((20, 520, 120), (100, 560, 90), (900, 540, 130)):
        for k in range(4):
            w = 40 - k * 7
            y = ty - k * h // 4
            pygame.draw.polygon(s, (16, 30, 24), [(tx - w, y), (tx + w, y), (tx, y - h // 3)])
            pygame.draw.line(s, (220, 225, 235), (tx - w + 6, y - 2), (tx - 4, y - h // 3 + 8), 2)
    draw_shadow(s, 480, 560)
    draw_person(s, 480, 560, "detective", RED, body=PLAYER_PURPLE)


def scene_carnival(s, fonts):
    vertical_gradient(s, (0, 0, WIDTH, HEIGHT), (10, 8, 30), (56, 22, 62))
    rng = random.Random(5)
    for _ in range(70):
        pygame.draw.circle(s, (230, 220, 255), (rng.randint(0, WIDTH), rng.randint(0, 250)), 1)
    # ferris wheel
    cx, cy, r = 200, 250, 150
    pygame.draw.line(s, (60, 50, 70), (cx, cy), (cx - 90, 480), 6)
    pygame.draw.line(s, (60, 50, 70), (cx, cy), (cx + 90, 480), 6)
    pygame.draw.circle(s, (80, 66, 90), (cx, cy), r, 4)
    pygame.draw.circle(s, (80, 66, 90), (cx, cy), r - 20, 2)
    for k in range(12):
        a = k * math.pi / 6
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        pygame.draw.line(s, (70, 58, 80), (cx, cy), (ex, ey), 2)
        pygame.draw.rect(s, BULB_COLORS[k % 5], (ex - 10, ey + 4, 20, 14), border_radius=4)
    for k in range(36):
        a = k * math.pi / 18
        bx, by = cx + r * math.cos(a), cy + r * math.sin(a)
        pygame.draw.circle(s, BULB_COLORS[k % 5], (int(bx), int(by)), 3)
    glow(s, (cx, cy), 60, (255, 210, 90), 60)
    # big top tent
    peak = (670, 130)
    left, right = 470, 870
    for k in range(10):
        x1 = left + k * (right - left) / 10
        x2 = left + (k + 1) * (right - left) / 10
        color = (170, 40, 52) if k % 2 == 0 else (230, 216, 196)
        pygame.draw.polygon(s, color, [peak, (x1, 320), (x2, 320)])
        pygame.draw.polygon(s, shade(color, -30), [(x1, 320), (x2, 320), (x2, 470), (x1, 470)])
    for k in range(10):
        x = left + k * 40 + 20
        pygame.draw.circle(s, (230, 216, 196), (int(x), 322), 18, 0, draw_bottom_left=True,
                           draw_bottom_right=True)
    pygame.draw.line(s, (60, 40, 30), peak, (670, 90), 4)
    pygame.draw.polygon(s, RED, [(670, 90), (705, 100), (670, 110)])
    pygame.draw.polygon(s, (20, 10, 14), [(630, 470), (670, 370), (710, 470)])
    glow(s, (670, 450), 60, (255, 205, 120), 90)
    draw_string_lights(s, (0, 110), (470, 300), 60, 0)
    draw_string_lights(s, (870, 300), (960, 200), 20, 0, 5)
    pygame.draw.rect(s, (22, 16, 26), (0, 470, WIDTH, 130))
    pygame.draw.polygon(s, (40, 30, 40), [(600, 470), (740, 470), (820, 600), (520, 600)])
    # ticket booth
    pygame.draw.rect(s, (110, 30, 40), (380, 390, 70, 80))
    pygame.draw.polygon(s, (230, 216, 196), [(370, 390), (460, 390), (415, 360)])
    pygame.draw.rect(s, (255, 205, 120), (392, 408, 46, 26))
    draw_text(s, "TICKETS", fonts[0], (230, 216, 196), (415, 448), center=True)
    draw_shadow(s, 320, 545)
    draw_person(s, 320, 545, "detective", RED, body=PLAYER_PURPLE)


SCENES = {"city": scene_city, "hotel": scene_hotel, "manor": scene_manor,
          "train": scene_train, "carnival": scene_carnival}


# --------------------------------------------------------------------------
# Game
# --------------------------------------------------------------------------

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Shadow Detective")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_title = load_font(52, bold=True)
        self.font_big = load_font(28, bold=True)
        self.font = load_font(18)
        self.font_bold = load_font(18, bold=True)
        self.font_small = load_font(14)
        self.font_small_bold = load_font(14, bold=True)
        self.font_tiny = load_font(11, bold=True)
        self.scenes = {}
        for name, builder in SCENES.items():
            surface = pygame.Surface((WIDTH, HEIGHT))
            builder(surface, (self.font_small, self.font_big))
            self.scenes[name] = surface
        self.vignette = self.build_vignette()
        self.tints = {}
        self.particles = [[random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
                           random.uniform(0.6, 1.4), random.uniform(0, 6.3)] for _ in range(170)]
        self.motes = [[random.uniform(0, WIDTH), random.uniform(TOP_BAR, HEIGHT),
                       random.uniform(0, 6.3)] for _ in range(28)]
        self.t = 0.0
        self.flash = 0.0
        self.highscore = self.load_highscore()
        self.new_highscore = False
        self.menu_index = 0
        self.new_game()

    def load_highscore(self):
        try:
            with open(HIGHSCORE_FILE) as f:
                return int(f.read().strip() or 0)
        except (OSError, ValueError):
            return 0

    def record_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            self.new_highscore = True
            try:
                with open(HIGHSCORE_FILE, "w") as f:
                    f.write(str(self.score))
            except OSError:
                pass

    def build_vignette(self):
        small = pygame.Surface((96, 60), pygame.SRCALPHA)
        for y in range(60):
            for x in range(96):
                dx = (x - 47.5) / 48
                dy = (y - 29.5) / 30
                d = min(1.0, math.sqrt(dx * dx + dy * dy))
                small.set_at((x, y), (0, 0, 0, int(170 * d ** 2.2)))
        return pygame.transform.smoothscale(small, (WIDTH, HEIGHT))

    def new_game(self):
        self.case_index = 0
        self.stars = []
        self.howto_return = "case_intro"
        self.menu_return = None
        self.resume_state = None
        self.score = 0
        self.new_highscore = False
        self.start_case()
        self.state = "title"

    def start_case(self, restart=False):
        # a restarted case gives back the points earned in it, so nobody can farm points
        if restart:
            self.score = self.case_start_score
        else:
            self.case_start_score = self.score
        self.case = CASES[self.case_index]
        self.theme = self.case["theme"]
        self.clues = self.case["clues"]
        self.suspects = self.case["suspects"]
        self.room = self.case["start"]
        self.found = []
        self.mistakes = 0
        self.message = None
        self.talk_id = None
        self.talk_text = ""
        self.asked = set()
        self.accuse_step = "suspect"
        self.accuse_suspect = None
        self.selected = []
        self.result = None
        self.file_first = True
        self.bumps = 0
        self.bonus = 0
        self.px, self.py = 480.0, 520.0
        self.walk = 0.0
        self.invulnerable = 0.0
        self.floaters = []
        self.spawn_enemies()
        self.state = "case_intro"

    def attempts_left(self):
        return self.case["attempts"] - self.mistakes

    # ------------------------------------------------------------------ loop

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.t += dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
            self.update(dt)
            self.draw()
            pygame.display.flip()

    def update(self, dt):
        weather = self.theme["weather"] if self.state != "title" else "rain"
        speed = {"rain": 650, "snow": 60, "confetti": 45}[weather]
        for p in self.particles:
            p[1] += speed * p[2] * dt
            p[0] -= speed * p[2] * dt * (0.25 if weather == "rain" else 0)
            p[3] += dt * 2
            if p[1] > HEIGHT:
                p[0] = random.uniform(0, WIDTH + 150)
                p[1] = random.uniform(-40, 0)
        for m in self.motes:
            m[1] -= dt * 6
            m[2] += dt
            if m[1] < TOP_BAR:
                m[1] = HEIGHT
                m[0] = random.uniform(0, WIDTH)
        self.flash = max(0.0, self.flash - dt * 3)
        if random.random() < dt / 6:
            self.flash = 1.0
        for f in self.floaters:
            f[3] += dt
        self.floaters = [f for f in self.floaters if f[3] < 1.2]
        if self.state == "explore":
            self.update_player(dt)
            self.update_enemies(dt)

    # ---------------------------------------------------------------- player

    def update_player(self, dt):
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        if dx and dy:
            dx, dy = dx * 0.707, dy * 0.707
        self.px += dx * PLAYER_SPEED * dt
        self.py += dy * PLAYER_SPEED * 0.6 * dt
        self.py = max(PLAYER_TOP, min(PLAYER_BOTTOM, self.py))
        self.walk = self.walk + dt * 11 if (dx or dy) else 0.0
        self.invulnerable = max(0.0, self.invulnerable - dt)
        # walking out at the left or right edge goes through the door on that side
        if self.px < 24 or self.px > WIDTH - 24:
            side_left = self.px < 24
            for door in self.case["rooms"][self.room]["doors"]:
                if (pygame.Rect(door["rect"]).centerx < WIDTH // 2) == side_left:
                    self.enter_room(door["to"])
                    return
            self.px = max(24, min(WIDTH - 24, self.px))

    def enter_room(self, new_room):
        old_room = self.room
        self.room = new_room
        self.px = 480
        for door in self.case["rooms"][new_room]["doors"]:
            if door["to"] == old_room:
                self.px = 80 if pygame.Rect(door["rect"]).centerx < WIDTH // 2 else WIDTH - 80
        self.py = max(PLAYER_TOP, min(PLAYER_BOTTOM, self.py))
        self.invulnerable = max(self.invulnerable, 0.8)
        self.spawn_enemies()

    def spawn_enemies(self):
        theme = self.theme
        self.enemies = []
        for i in range(theme["enemies"]):
            x = random.uniform(120, 840)
            for _ in range(30):
                if abs(x - self.px) > 230:
                    break
                x = random.uniform(120, 840)
            lane = 462 + (i * 41) % 118
            speed = theme["enemy_speed"] * random.uniform(0.85, 1.15)
            if theme["enemy_mode"] == "bounce":
                angle = random.uniform(0.35, 1.0) * random.choice([-1, 1])
                vx = math.cos(angle) * speed * random.choice([-1, 1])
                vy = math.sin(angle) * speed * 0.6
            else:
                vx, vy = speed * random.choice([-1, 1]), 0.0
            self.enemies.append([x, lane, vx, vy, random.uniform(0, 5)])

    def update_enemies(self, dt):
        for e in self.enemies:
            e[0] += e[2] * dt
            e[1] += e[3] * dt
            e[4] += dt
            if not 90 < e[0] < WIDTH - 90:
                e[2] = -e[2]
                e[0] = max(90, min(WIDTH - 90, e[0]))
            if not 456 < e[1] < 588:
                e[3] = -e[3]
                e[1] = max(456, min(588, e[1]))
        if self.invulnerable > 0:
            return
        for e in self.enemies:
            if abs(e[0] - self.px) < 40 and abs(e[1] - self.py) < 18:
                self.hit_by(e)
                break

    def hit_by(self, enemy):
        # bumping into an obstacle costs points and pushes the player back - nobody dies
        self.bumps += 1
        self.add_points(POINTS_HIT, self.px, self.py - 200)
        self.invulnerable = 1.6
        push = 70 if self.px >= enemy[0] else -70
        self.px = max(30, min(WIDTH - 30, self.px + push))

    def add_points(self, points, x, y):
        self.score = max(0, self.score + points)
        text = ("+%d" % points) if points > 0 else str(points)
        self.floaters.append([text, x, y, 0.0, YELLOW if points > 0 else RED])

    def nearby_spot(self):
        best, best_dist = None, 10 ** 9
        for spot in self.hotspots():
            r = spot["rect"]
            if not r.left - 30 <= self.px <= r.right + 30:
                continue
            if spot["kind"] == "talk":
                if abs(self.py - spot["feet"]) > 70:
                    continue
            elif r.bottom > FLOOR_Y + 5:
                if not r.top - 20 <= self.py <= r.bottom + 50:
                    continue
            elif self.py > FLOOR_Y + 75:
                continue
            dist = abs(self.px - r.centerx) + (40 if spot["kind"] == "door" else 0)
            if dist < best_dist:
                best, best_dist = spot, dist
        return best

    def use_spot(self, spot):
        kind = spot["kind"]
        if kind == "clue":
            if spot.get("needs") and spot["needs"] not in self.found:
                self.show_message(*spot["locked"])
                return
            cid = spot["clue"]
            new = cid not in self.found
            if new:
                self.found.append(cid)
                self.add_points(POINTS_CLUE, self.px, self.py - 200)
            title, text = self.clues[cid]
            self.show_message(title, text, "New clue added to your notebook! +%d points" % POINTS_CLUE
                              if new else None)
        elif kind == "look":
            self.show_message(*spot["look"])
        elif kind == "door":
            self.enter_room(spot["to"])
        elif kind == "talk":
            self.talk_id = spot["who"]
            self.talk_text = self.suspects[spot["who"]]["greeting"]
            self.state = "talk"

    # ----------------------------------------------------------------- input

    def handle_key(self, key):
        state = self.state
        if state == "title":
            if self.resume_state:
                if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_c):
                    self.state = self.resume_state
                elif key == pygame.K_n:
                    self.new_game()
                    self.open_howto("case_intro")
            elif key != pygame.K_ESCAPE:
                self.open_howto("case_intro")      # welcome screen: press any key
        elif state == "howto":
            self.state = self.howto_return
        elif state == "menu":
            if key == pygame.K_ESCAPE:
                self.state = self.menu_return
            elif key == pygame.K_UP:
                self.menu_index = (self.menu_index - 1) % len(self.MENU_ITEMS)
            elif key == pygame.K_DOWN:
                self.menu_index = (self.menu_index + 1) % len(self.MENU_ITEMS)
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                self.activate_menu(self.MENU_ITEMS[self.menu_index][0])
        elif state == "message":
            if key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                self.close_message()
        elif state == "case_intro":
            if key == pygame.K_ESCAPE:
                self.open_menu()
            else:
                self.file_first = True
                self.state = "case_file"
        elif state == "case_file":
            if key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_f):
                self.file_first = False
                self.state = "explore"
        elif state == "notebook":
            if key in (pygame.K_n, pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                self.state = "explore"
        elif state == "talk":
            if key == pygame.K_ESCAPE:
                self.state = "explore"
            elif pygame.K_1 <= key <= pygame.K_9:
                options = self.talk_options()
                number = key - pygame.K_1
                if number < len(options):
                    self.choose_topic(options[number][0][0])
        elif state == "accuse":
            if key == pygame.K_ESCAPE:
                self.state = "explore"
        elif state in ("ending", "finale"):
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.end_button_pressed()
            elif key == pygame.K_x:
                self.exit_to_title()
            elif key == pygame.K_ESCAPE:
                self.open_menu()
        elif state == "explore":
            if key == pygame.K_ESCAPE:
                self.open_menu()
            elif key == pygame.K_SPACE:
                spot = self.nearby_spot()
                if spot:
                    self.use_spot(spot)
            elif key == pygame.K_n:
                self.state = "notebook"
            elif key == pygame.K_a:
                self.start_accuse()
            elif key == pygame.K_f:
                self.file_first = False
                self.state = "case_file"
            elif key == pygame.K_h:
                self.open_howto("explore")

    def exit_to_title(self):
        """Leave the current screen and go back to the welcome screen (the window stays open)."""
        self.record_highscore()
        if self.state == "finale":
            self.new_game()                 # all cases done - start fresh next time
        else:
            self.resume_state = self.state  # "Continue" brings you back here
            self.state = "title"

    def quit(self):
        self.record_highscore()
        pygame.quit()
        sys.exit()

    def open_howto(self, back_to):
        self.howto_return = back_to
        self.state = "howto"

    def handle_click(self, pos):
        if self.state in ("case_intro", "case_file", "ending", "finale") \
                and self.corner_menu_button().collidepoint(pos):
            self.open_menu()
            return
        if self.state == "menu":
            self.click_menu(pos)
        elif self.state == "title":
            self.click_title(pos)
        elif self.state == "howto":
            self.state = self.howto_return
        elif self.state == "case_intro":
            self.file_first = True
            self.state = "case_file"
        elif self.state == "case_file":
            self.file_first = False
            self.state = "explore"
        elif self.state == "message":
            self.close_message()
        elif self.state == "notebook":
            self.state = "explore"
        elif self.state == "explore":
            self.click_explore(pos)
        elif self.state == "talk":
            self.click_talk(pos)
        elif self.state == "accuse":
            self.click_accuse(pos)
        elif self.state in ("ending", "finale"):
            if self.end_button_rect().collidepoint(pos):
                self.end_button_pressed()
            elif self.exit_button_rect().collidepoint(pos):
                self.exit_to_title()

    def click_explore(self, pos):
        if self.menu_button().collidepoint(pos):
            self.open_menu()
            return
        if self.file_button().collidepoint(pos):
            self.file_first = False
            self.state = "case_file"
            return
        if self.notebook_button().collidepoint(pos):
            self.state = "notebook"
            return
        if self.accuse_button().collidepoint(pos):
            self.start_accuse()

    def show_message(self, title, text, note=None, after="explore"):
        self.message = {"title": title, "text": text, "note": note, "after": after}
        self.state = "message"

    def close_message(self):
        self.state = self.message["after"]
        self.message = None

    # ------------------------------------------------------------------ menu

    MENU_ITEMS = [("resume", "Resume"), ("howto", "How to Play"),
                  ("restart", "Restart Case"), ("exit", "Exit to Title Screen")]

    def open_menu(self):
        self.menu_return = self.state
        self.menu_index = 0
        self.state = "menu"

    def corner_menu_button(self):
        return pygame.Rect(846, 4, 108, 28)

    def menu_buttons(self):
        return [(key, label, pygame.Rect(360, 196 + i * 60, 240, 46))
                for i, (key, label) in enumerate(self.MENU_ITEMS)]

    def click_menu(self, pos):
        for key, _, rect in self.menu_buttons():
            if rect.collidepoint(pos):
                self.activate_menu(key)

    def activate_menu(self, key):
        if key == "resume":
            self.state = self.menu_return
        elif key == "howto":
            self.open_howto("menu")
        elif key == "restart":
            self.start_case(restart=True)
        elif key == "exit":
            self.state = self.menu_return
            self.exit_to_title()

    def draw_menu(self, s, mouse):
        shade_screen(s, 170)
        box = pygame.Rect(320, 100, 320, 370)
        panel(s, box, 240)
        draw_text(s, "PAUSED", self.font_big, GOLD, (WIDTH // 2, 140), center=True)
        draw_text(s, "Case %d: %s" % (self.case_index + 1, self.case["title"]),
                  self.font_small, LIGHT_GREY, (WIDTH // 2, 168), center=True)
        for i, (key, label, rect) in enumerate(self.menu_buttons()):
            color = RED if key in ("restart", "exit") else GOLD
            if i == self.menu_index:
                pygame.draw.rect(s, WHITE, rect.inflate(8, 8), 2, border_radius=8)
            self.draw_button(s, rect, label, mouse, color)
        draw_text(s, "Arrows + SPACE to choose  -  Esc: back", self.font_small, GREY,
                  (WIDTH // 2, 448), center=True)

    def continue_button(self):
        return pygame.Rect(330, 470, 300, 46)

    def new_game_button(self):
        return pygame.Rect(330, 526, 300, 46)

    def click_title(self, pos):
        if not self.resume_state:
            self.open_howto("case_intro")
        elif self.continue_button().collidepoint(pos):
            self.state = self.resume_state
        elif self.new_game_button().collidepoint(pos):
            self.new_game()
            self.open_howto("case_intro")

    # --------------------------------------------------------------- top bar

    def menu_button(self):
        return pygame.Rect(478, 8, 34, 34)

    def file_button(self):
        return pygame.Rect(520, 8, 100, 34)

    def notebook_button(self):
        return pygame.Rect(628, 8, 160, 34)

    def accuse_button(self):
        return pygame.Rect(796, 8, 150, 34)

    def draw_button(self, s, rect, label, mouse, color=GOLD, enabled=True):
        if not enabled:
            pygame.draw.rect(s, DARK, rect, border_radius=6)
            pygame.draw.rect(s, (55, 56, 60), rect, 2, border_radius=6)
            draw_text(s, label, self.font, (80, 80, 85), rect.center, center=True)
            return
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(s, (40, 34, 20) if hover else DARK, rect, border_radius=6)
        pygame.draw.rect(s, color, rect, 2, border_radius=6)
        draw_text(s, label, self.font, WHITE if hover else color, rect.center, center=True)

    def draw_top_bar(self, s, mouse):
        pygame.draw.rect(s, BLACK, (0, 0, WIDTH, TOP_BAR))
        pygame.draw.line(s, GOLD, (0, TOP_BAR - 1), (WIDTH, TOP_BAR - 1), 1)
        room_name = self.case["rooms"][self.room]["name"]
        name_font = self.font_big if self.font_big.size(room_name)[0] < 300 else self.font_bold
        draw_text(s, room_name, name_font, GOLD, (18, 8 if name_font is self.font_big else 14))
        draw_text(s, "Case %d of %d" % (self.case_index + 1, len(CASES)),
                  self.font_small_bold, LIGHT_GREY, (325, 3))
        draw_text(s, "Clues: %d/%d  (need %d)" % (len(self.found), len(self.clues),
                                                 self.case["min_clues"]),
                  self.font_small, WHITE, (325, 18))
        draw_text(s, "Attempts left: %d" % self.attempts_left(),
                  self.font_small, LIGHT_GREY, (325, 33))
        self.draw_button(s, self.menu_button(), "", mouse)
        for k in range(3):
            pygame.draw.line(s, GOLD, (486, 17 + k * 8), (503, 17 + k * 8), 2)
        self.draw_button(s, self.file_button(), "File [F]", mouse)
        self.draw_button(s, self.notebook_button(), "Notebook [N]", mouse)
        self.draw_button(s, self.accuse_button(), "Accuse [A]", mouse, RED)

    # -------------------------------------------------------------- hotspots

    def hotspots(self):
        room = self.case["rooms"][self.room]
        spots = []
        for spot in room["spots"]:
            entry = dict(spot)
            entry["rect"] = pygame.Rect(spot["rect"])
            entry["kind"] = "clue" if "clue" in spot else "look"
            spots.append(entry)
        for who, x, fy, behind in room["people"]:
            sus = self.suspects[who]
            # people behind a desk or table can only be clicked above it
            height = 110 if behind else 195
            spots.append({"rect": pygame.Rect(x - 40, fy - 195, 80, height), "kind": "talk", "feet": fy,
                          "who": who, "label": "%s, %s" % (sus["name"], sus["role"])})
        for door in room["doors"]:
            spots.append({"rect": pygame.Rect(door["rect"]), "kind": "door", "to": door["to"],
                          "label": "Go to: " + self.case["rooms"][door["to"]]["name"]})
        return spots

    # ---------------------------------------------------------------- rooms

    def draw_room(self, s):
        room = self.case["rooms"][self.room]
        self.draw_wall(s, room)
        self.draw_floor(s, room)
        strength = self.case["glow"]
        if strength > 0:
            for spot in room["spots"]:
                if "clue" in spot and spot["clue"] not in self.found:
                    r = pygame.Rect(spot["rect"])
                    radius = min(60, max(30, min(r.w, r.h) // 2 + 15))
                    alpha = (55 + 35 * math.sin(self.t * 3)) * strength
                    glow(s, r.center, radius, spot.get("color", GOLD), alpha)
        for who, x, fy, behind in room["people"]:
            if behind:
                sus = self.suspects[who]
                draw_person(s, x, fy, sus["style"], sus["accent"])
        getattr(self, "draw_" + room["draw"])(s)
        for door in room["doors"]:
            self.draw_door(s, door["rect"], door["sign"], door.get("ajar", False))
        for spot in room["spots"]:
            if "clue" in spot and spot["clue"] in self.found:
                draw_tick(s, pygame.Rect(spot["rect"]).topright)
        # people, obstacles and the player are drawn from back to front
        actors = []
        for who, x, fy, behind in room["people"]:
            if not behind:
                actors.append((fy, "person", (who, x, fy)))
        for e in self.enemies:
            actors.append((e[1], "enemy", e))
        actors.append((self.py, "player", None))
        for _, kind, data in sorted(actors, key=lambda a: a[0]):
            if kind == "person":
                who, x, fy = data
                sus = self.suspects[who]
                draw_shadow(s, x, fy)
                draw_person(s, x, fy, sus["style"], sus["accent"])
            elif kind == "enemy":
                draw_enemy(s, self.theme["enemy"], data[0], data[1], data[4], data[2])
            else:
                self.draw_player(s)
        self.draw_atmosphere(s)

    def draw_player(self, s):
        x, y = int(self.px), int(self.py)
        if self.invulnerable > 0 and int(self.invulnerable * 12) % 2 == 0:
            return
        alpha_ellipse(s, PLAYER_PURPLE, 90, (x - 46, y - 12, 92, 24))
        pygame.draw.ellipse(s, (190, 130, 255), (x - 40, y - 9, 80, 18), 2)
        draw_person(s, x, y, "detective", RED, body=PLAYER_PURPLE, step=math.sin(self.walk))

    def draw_prompt(self, s):
        spot = self.nearby_spot()
        if not spot:
            return
        pygame.draw.rect(s, (220, 220, 230), spot["rect"], 1, border_radius=4)
        verb = {"clue": "Examine: ", "look": "Examine: ", "talk": "Talk to ", "door": ""}[spot["kind"]]
        img = self.font_small_bold.render("[SPACE]  " + verb + spot["label"], True, WHITE)
        box = img.get_rect().inflate(16, 10)
        box.midbottom = (int(self.px), int(self.py) - 210)
        box.clamp_ip(pygame.Rect(4, TOP_BAR + 4, WIDTH - 8, HEIGHT))
        panel(s, box, 230, (190, 130, 255))
        s.blit(img, img.get_rect(center=box.center))

    def draw_hud(self, s):
        box = pygame.Rect(8, TOP_BAR + 8, 300, 32)
        panel(s, box, 200, GREY)
        draw_text(s, "Score: %d" % self.score, self.font_bold, YELLOW, (box.x + 12, box.y + 5))
        draw_text(s, "Bumps: %d" % self.bumps, self.font_small, LIGHT_GREY, (box.x + 190, box.y + 8))
        for text, x, y, age, color in self.floaters:
            img = self.font_big.render(text, True, color)
            img.set_alpha(int(255 * (1 - age / 1.2)))
            s.blit(img, img.get_rect(center=(int(x), int(y - age * 60))))

    def draw_atmosphere(self, s):
        # floating dust in the light
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x, y, phase in self.motes:
            a = int(40 + 30 * math.sin(phase * 2))
            pygame.draw.circle(layer, (230, 225, 200, a), (int(x + 6 * math.sin(phase)), int(y)), 1)
        s.blit(layer, (0, 0))
        # colour mood of the case
        tint = self.theme["tint"]
        if self.case_index not in self.tints:
            t = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            t.fill(tint)
            self.tints[self.case_index] = t
        s.blit(self.tints[self.case_index], (0, 0))
        if self.theme.get("lightning") and self.flash > 0.3:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((210, 220, 255, int(45 * self.flash)))
            s.blit(flash, (0, 0))
        s.blit(self.vignette, (0, 0))

    def draw_wall(self, s, room):
        wall = room["wall"]
        style = room.get("wall_style", self.theme["wall_style"])
        top = TOP_BAR + 22
        pygame.draw.rect(s, wall, (0, TOP_BAR, WIDTH, FLOOR_Y - TOP_BAR))
        if style == "wallpaper":
            for x in range(0, WIDTH, 32):
                pygame.draw.rect(s, shade(wall, 7), (x, top, 14, 300 - top))
                for y in range(top + 20, 290, 44):
                    pygame.draw.polygon(s, shade(wall, 14), [(x + 23, y - 5), (x + 28, y),
                                                             (x + 23, y + 5), (x + 18, y)])
        if style in ("wainscot", "wallpaper"):
            pygame.draw.rect(s, shade(wall, -14), (0, 300, WIDTH, FLOOR_Y - 300))
            pygame.draw.rect(s, shade(wall, 18), (0, 296, WIDTH, 6))
            for x in range(14, WIDTH, 112):
                pygame.draw.rect(s, shade(wall, -26), (x, 314, 92, 100), 2)
                pygame.draw.line(s, shade(wall, 4), (x + 2, 413), (x + 91, 413), 1)
        elif style == "brick":
            for row, y in enumerate(range(top, FLOOR_Y, 22)):
                pygame.draw.line(s, shade(wall, -14), (0, y), (WIDTH, y), 2)
                off = 0 if row % 2 == 0 else 30
                for x in range(off, WIDTH, 60):
                    pygame.draw.line(s, shade(wall, -14), (x, y), (x, y + 22), 2)
                    if (x * 7 + row * 13) % 5 == 0:
                        pygame.draw.rect(s, shade(wall, 6), (x + 2, y + 2, 56, 18))
        elif style == "train":
            pygame.draw.rect(s, shade(wall, -18), (0, 310, WIDTH, FLOOR_Y - 310))
            pygame.draw.rect(s, BRASS, (0, 306, WIDTH, 4))
            for x in range(0, WIDTH, 120):
                pygame.draw.line(s, shade(wall, -12), (x, top), (x, FLOOR_Y), 2)
                pygame.draw.line(s, shade(wall, 10), (x + 3, top), (x + 3, FLOOR_Y), 1)
            # curved ceiling and luggage rack
            pygame.draw.rect(s, shade(wall, -30), (0, TOP_BAR, WIDTH, 26))
            pygame.draw.ellipse(s, shade(wall, -10), (-60, TOP_BAR - 20, WIDTH + 120, 70))
            for x in range(0, WIDTH, 6):
                pygame.draw.line(s, (120, 100, 60), (x, 92), (x, 98), 1)
            pygame.draw.line(s, BRASS, (0, 92), (WIDTH, 92), 3)
            pygame.draw.line(s, BRASS, (0, 99), (WIDTH, 99), 2)
        elif style == "metal":
            for y in range(top, FLOOR_Y, 90):
                for x in range(0, WIDTH, 160):
                    pygame.draw.rect(s, shade(wall, -10), (x, y, 160, 90), 2)
                    for rx, ry in ((x + 8, y + 8), (x + 152, y + 8), (x + 8, y + 82), (x + 152, y + 82)):
                        pygame.draw.circle(s, shade(wall, 20), (rx, ry), 3)
        elif style == "tent":
            second = room.get("wall2", shade(wall, 40))
            for i, x in enumerate(range(0, WIDTH, 60)):
                color = wall if i % 2 == 0 else second
                pygame.draw.polygon(s, color, [(x, TOP_BAR), (x + 60, TOP_BAR), (x + 64, FLOOR_Y), (x - 4, FLOOR_Y)])
                pygame.draw.line(s, shade(color, -25), (x + 58, TOP_BAR), (x + 62, FLOOR_Y), 3)
            for x in range(0, WIDTH, 60):
                pygame.draw.circle(s, shade(wall, -25), (x + 30, TOP_BAR + 6), 30, 0,
                                   draw_bottom_left=True, draw_bottom_right=True)
                pygame.draw.circle(s, GOLD, (x + 30, TOP_BAR + 36), 3)
        elif style == "drape":
            for x in range(0, WIDTH, 24):
                pygame.draw.line(s, shade(wall, 10 if (x // 24) % 2 else -8), (x, TOP_BAR), (x + 6, FLOOR_Y), 8)
            rng = random.Random(7)
            for _ in range(40):
                sx, sy = rng.randint(0, WIDTH), rng.randint(TOP_BAR + 30, 300)
                a = 120 + int(100 * math.sin(self.t * 2 + sx))
                pygame.draw.circle(s, (min(255, a + 60), min(255, a + 30), 80), (sx, sy), 2)
        elif style == "night":
            vertical_gradient(s, (0, TOP_BAR, WIDTH, FLOOR_Y - TOP_BAR), (8, 8, 26), (46, 24, 56))
            rng = random.Random(11)
            for _ in range(80):
                sx, sy = rng.randint(0, WIDTH), rng.randint(TOP_BAR, 330)
                twinkle = 150 + int(90 * math.sin(self.t * 3 + sx * 0.1))
                pygame.draw.circle(s, (twinkle, twinkle, min(255, twinkle + 30)), (sx, sy), 1)
            return
        if style not in ("tent", "drape"):
            pygame.draw.rect(s, shade(wall, -22), (0, TOP_BAR, WIDTH, 22))
            pygame.draw.line(s, shade(wall, 22), (0, top), (WIDTH, top), 2)
            pygame.draw.line(s, shade(wall, -30), (0, top + 3), (WIDTH, top + 3), 1)

    def draw_floor(self, s, room):
        color = room.get("floor_color", self.theme["floor_color"])
        style = room.get("floor", self.theme["floor"])
        pygame.draw.rect(s, color, (0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y))
        rows = [430, 442, 457, 476, 500, 530, 566, 600]
        if style == "tiles":
            for i, y in enumerate(rows):
                pygame.draw.line(s, shade(color, 12), (0, y), (WIDTH, y), 2)
            for i in range(-7, 8):
                pygame.draw.line(s, shade(color, 12), (480 + i * 85, FLOOR_Y), (480 + i * 230, HEIGHT), 2)
        elif style in ("wood", "planks"):
            rng = random.Random(2)
            step = 1 if style == "wood" else 2
            for i in range(0, len(rows) - 1, step):
                y1 = rows[i]
                y2 = rows[min(i + step, len(rows) - 1)]
                tone = shade(color, rng.randint(-6, 6))
                pygame.draw.rect(s, tone, (0, y1, WIDTH, y2 - y1))
                pygame.draw.line(s, shade(color, -18), (0, y1), (WIDTH, y1), 2)
                pygame.draw.line(s, shade(color, 10), (0, y1 + 2), (WIDTH, y1 + 2), 1)
                x = rng.randint(0, 200)
                while x < WIDTH:
                    pygame.draw.line(s, shade(color, -18), (x, y1), (x, y2), 2)
                    x += rng.randint(160, 320)
        elif style == "carpet":
            rug = [(130, 444), (830, 444), (930, 596), (30, 596)]
            pygame.draw.polygon(s, shade(color, 14), rug)
            pygame.draw.polygon(s, (150, 118, 66), rug, 3)
            inner = [(160, 452), (800, 452), (888, 588), (72, 588)]
            pygame.draw.polygon(s, (150, 118, 66), inner, 1)
            for k in range(12):
                f = (k + 0.5) / 12
                dx = 160 + (800 - 160) * f
                pygame.draw.polygon(s, shade(color, 30), [(dx, 456), (dx + 6, 462), (dx, 468), (dx - 6, 462)])
        elif style == "concrete":
            rng = random.Random(8)
            for _ in range(12):
                x, y = rng.randint(0, WIDTH), rng.randint(FLOOR_Y + 10, HEIGHT)
                alpha_ellipse(s, BLACK, 40, (x, y, rng.randint(40, 120), rng.randint(10, 26)))
            for _ in range(5):
                x, y = rng.randint(0, WIDTH), rng.randint(FLOOR_Y, HEIGHT - 30)
                pygame.draw.lines(s, shade(color, -16), False,
                                  [(x, y), (x + 20, y + 12), (x + 26, y + 30), (x + 50, y + 38)], 1)
        elif style == "sawdust":
            rng = random.Random(6)
            for _ in range(500):
                x, y = rng.randint(0, WIDTH), rng.randint(FLOOR_Y, HEIGHT)
                pygame.draw.circle(s, shade(color, rng.randint(-25, 25)), (x, y), 1)
        elif style == "grass":
            rng = random.Random(12)
            for _ in range(260):
                x, y = rng.randint(0, WIDTH), rng.randint(FLOOR_Y + 4, HEIGHT)
                h = 4 + (y - FLOOR_Y) // 20
                pygame.draw.line(s, shade(color, rng.randint(0, 25)), (x, y), (x + rng.randint(-3, 3), y - h), 1)
        elif style == "stone":
            for i, y in enumerate(rows):
                pygame.draw.line(s, shade(color, -14), (0, y), (WIDTH, y), 2)
                off = (i * 53) % 140
                y2 = rows[min(i + 1, len(rows) - 1)]
                for x in range(off, WIDTH, 140 + i * 12):
                    pygame.draw.line(s, shade(color, -14), (x, y), (x, y2), 2)
        pygame.draw.rect(s, DARK, (0, FLOOR_Y - 8, WIDTH, 8))
        pygame.draw.line(s, shade(room["wall"], 15), (0, FLOOR_Y - 8), (WIDTH, FLOOR_Y - 8), 1)

    def draw_door(self, s, rect, label, ajar=False):
        r = pygame.Rect(rect)
        kind = self.theme["door"]
        if kind == "flap":
            pygame.draw.rect(s, (14, 10, 16), r)
            glow(s, r.center, 60, (255, 205, 120), 40)
            pygame.draw.polygon(s, (150, 40, 50), [r.topleft, (r.x + 40, r.y), (r.x + 20, r.bottom), r.bottomleft])
            pygame.draw.polygon(s, (220, 205, 185), [r.topright, (r.right - 40, r.y), (r.right - 20, r.bottom), r.bottomright])
            pygame.draw.line(s, GOLD, (r.x + 6, r.centery), (r.x + 30, r.centery + 10), 3)
            pygame.draw.line(s, GOLD, (r.right - 6, r.centery), (r.right - 30, r.centery + 10), 3)
        elif kind == "train":
            pygame.draw.rect(s, (70, 48, 34), r)
            pygame.draw.rect(s, BRASS, r, 3)
            pane = pygame.Rect(r.x + 20, r.y + 18, r.w - 40, 70)
            pygame.draw.rect(s, (30, 40, 60), pane, border_radius=6)
            pygame.draw.rect(s, BRASS, pane, 2, border_radius=6)
            pygame.draw.polygon(s, (200, 210, 225), [pane.bottomleft, (pane.x + 18, pane.bottom), (pane.x, pane.bottom - 12)])
            pygame.draw.rect(s, BRASS, (r.right - 18, r.centery, 5, 40), border_radius=2)
            pygame.draw.rect(s, shade((70, 48, 34), -15), (r.x + 14, r.y + 110, r.w - 28, 70), 2)
        else:
            pygame.draw.rect(s, BLACK, r)
            if ajar:
                pygame.draw.polygon(s, (58, 52, 46), [r.topleft, (r.x + 65, r.y + 10),
                                                      (r.x + 65, r.bottom - 5), r.bottomleft])
                alpha_polygon(s, YELLOW, 80, [(r.x + 65, r.y + 10), r.topright,
                                              r.bottomright, (r.x + 65, r.bottom - 5)])
            else:
                pygame.draw.rect(s, (58, 50, 42), r.inflate(-12, -8))
                pygame.draw.rect(s, (48, 41, 35), (r.x + 18, r.y + 20, r.w - 36, 60))
                pygame.draw.rect(s, (48, 41, 35), (r.x + 18, r.y + 100, r.w - 36, 80))
                pygame.draw.line(s, (70, 62, 54), (r.x + 18, r.y + 20), (r.right - 18, r.y + 20), 1)
                pygame.draw.circle(s, LIGHT_GREY, (r.right - 20, r.centery + 10), 4)
            pygame.draw.rect(s, GREY, r, 4)
        sign = pygame.Rect(0, 0, 130, 20)
        sign.midbottom = (r.centerx, r.y - 6)
        pygame.draw.rect(s, DARK, sign)
        pygame.draw.rect(s, GREY, sign, 1)
        draw_text(s, label, self.font_tiny, LIGHT_GREY, sign.center, center=True)

    def draw_window(self, s, rect, lightning=False, mountains=False):
        """A window looking out into the weather of the current case."""
        r = pygame.Rect(rect)
        sky_top, sky_bottom = (22, 28, 44), (40, 48, 66)
        if lightning and self.flash > 0:
            sky_top = lerp_color(sky_top, (200, 210, 230), self.flash)
            sky_bottom = lerp_color(sky_bottom, (200, 210, 230), self.flash)
        vertical_gradient(s, r, sky_top, sky_bottom)
        s.set_clip(r)
        if mountains:
            peaks = [(r.x - 10, r.bottom - 20), (r.x + r.w * 0.3, r.y + 30), (r.x + r.w * 0.55, r.bottom - 40),
                     (r.x + r.w * 0.8, r.y + 20), (r.right + 10, r.bottom - 30)]
            pygame.draw.polygon(s, (58, 66, 90), peaks + [r.bottomright, r.bottomleft])
            for px, py in peaks[1:4:2]:
                pygame.draw.polygon(s, (220, 225, 235), [(px, py), (px - 16, py + 18), (px + 16, py + 18)])
            pygame.draw.rect(s, (200, 206, 218), (r.x, r.bottom - 16, r.w, 16))
        weather = self.theme["weather"]
        for i in range(max(6, r.w // 10)):
            if weather == "snow":
                x = r.x + (i * 37 + 10 * math.sin(self.t + i)) % r.w
                y = r.y + (i * 53 + self.t * (25 + i % 3 * 10)) % r.h
                pygame.draw.circle(s, (235, 238, 245), (int(x), int(y)), 1 + i % 2)
            else:
                x = r.x + (i * 37) % r.w + 10
                y = r.y + (i * 53 + self.t * 320) % (r.h + 20) - 10
                pygame.draw.line(s, (120, 130, 150), (x, y), (x - 3, y + 11), 1)
        alpha_polygon(s, (255, 255, 255), 18, [r.topleft, (r.x + r.w // 3, r.y), (r.x, r.y + r.h // 2)])
        s.set_clip(None)

    def draw_window_rain(self, s, rect, lightning=False):
        self.draw_window(s, rect, lightning)

    # ---- Case 1 rooms -----------------------------------------------------

    def draw_hall(self, s):
        draw_chandelier(s, 480, 100)
        pygame.draw.rect(s, (24, 25, 29), (400, 190, 160, 240))
        self.draw_window(s, (412, 205, 56, 130))
        self.draw_window(s, (492, 205, 56, 130))
        pygame.draw.rect(s, GREY, (400, 190, 160, 240), 4)
        pygame.draw.line(s, GREY, (480, 190), (480, 430), 4)
        pygame.draw.rect(s, BRASS, (470, 340, 6, 30))
        pygame.draw.rect(s, BRASS, (484, 340, 6, 30))
        draw_text(s, "CITY MUSEUM OF GREYHAVEN", self.font_small, LIGHT_GREY, (480, 165), center=True)

        # key board - one hook is empty
        pygame.draw.rect(s, WOOD, (185, 170, 160, 90))
        pygame.draw.rect(s, WOOD_DARK, (185, 170, 160, 90), 3)
        for i, lab in enumerate(["HALL", "OFFC", "STOR", "ROOF"]):
            hx = 208 + i * 38
            pygame.draw.circle(s, LIGHT_GREY, (hx, 188), 3)
            if lab == "STOR":
                color = RED if "key" not in self.found else (150, 70, 70)
            else:
                pygame.draw.line(s, LIGHT_GREY, (hx, 188), (hx, 200), 2)
                pygame.draw.circle(s, LIGHT_GREY, (hx, 210), 7, 3)
                pygame.draw.rect(s, LIGHT_GREY, (hx - 2, 216, 4, 10))
                color = GREY
            pygame.draw.rect(s, color, (hx - 17, 230, 34, 13))
            draw_text(s, lab, self.font_tiny, BLACK, (hx, 237), center=True)

        # camera and control panel
        pygame.draw.rect(s, DARK, (870, 72, 8, 24))
        pygame.draw.rect(s, (40, 41, 46), (826, 92, 52, 22))
        pygame.draw.rect(s, BLACK, (816, 96, 12, 14))
        pygame.draw.lines(s, BLACK, False, [(874, 114), (874, 140), (740, 140), (720, 160)], 2)
        pygame.draw.rect(s, (36, 37, 42), (620, 160, 120, 90), border_radius=4)
        pygame.draw.rect(s, BLACK, (632, 172, 96, 50))
        draw_text(s, "CAM 1", self.font_tiny, LIGHT_GREY, (638, 176))
        if "camera" in self.found or int(self.t * 2) % 2 == 0:
            draw_text(s, "OFF 22:10", self.font_small, YELLOW, (638, 194))
        for i in range(4):
            pygame.draw.circle(s, GREY, (640 + i * 25, 236), 5)

        # reception desk
        pygame.draw.rect(s, WOOD, (170, 395, 220, 70))
        pygame.draw.rect(s, (80, 64, 48), (162, 388, 236, 12))
        for px in (180, 280):
            pygame.draw.rect(s, WOOD_DARK, (px, 408, 90, 48), 2)
        pygame.draw.rect(s, PAPER, (220, 378, 40, 12))
        pygame.draw.rect(s, PAPER, (228, 372, 40, 12))

    def draw_exhibition(self, s):
        pygame.draw.rect(s, (91, 93, 99), (180, 120, 120, 150))
        pygame.draw.circle(s, (122, 124, 130), (240, 175), 25)
        pygame.draw.rect(s, (70, 72, 77), (205, 210, 70, 50))
        pygame.draw.rect(s, (139, 141, 146), (180, 120, 120, 150), 7)
        pygame.draw.rect(s, (85, 87, 92), (640, 120, 110, 90))
        pygame.draw.polygon(s, (110, 112, 118), [(650, 200), (690, 145), (730, 200)])
        pygame.draw.circle(s, (150, 150, 150), (715, 140), 8)
        pygame.draw.rect(s, (139, 141, 146), (640, 120, 110, 90), 7)
        pygame.draw.line(s, GREY, (0, 96), (WIDTH, 96), 2)

        pygame.draw.rect(s, BLACK, (465, TOP_BAR + 18, 30, 12))
        alpha_polygon(s, (255, 242, 196), 45, [(470, 80), (490, 80), (610, 430), (350, 430)])
        glow(s, (480, 195), 140, GOLD, 60)
        pygame.draw.rect(s, (43, 44, 48), (380, 110, 200, 170))
        pygame.draw.rect(s, (60, 61, 66), (395, 125, 170, 140), 1)
        pygame.draw.rect(s, GOLD, (380, 110, 200, 170), 12)
        pygame.draw.rect(s, shade(GOLD, 40), (380, 110, 200, 170), 2)
        pygame.draw.circle(s, LIGHT_GREY, (480, 104), 3)
        pygame.draw.rect(s, (200, 200, 200), (440, 290, 80, 18))
        draw_text(s, "The Moonlit Night", self.font_tiny, BLACK, (480, 299), center=True)

        for px in (360, 600):
            pygame.draw.rect(s, (150, 152, 158), (px - 3, 330, 6, 70))
            pygame.draw.ellipse(s, (150, 152, 158), (px - 14, 396, 28, 8))
            pygame.draw.circle(s, (150, 152, 158), (px, 328), 7)
        pygame.draw.lines(s, (110, 30, 40), False, [(363, 333), (390, 365), (420, 395)], 5)
        pygame.draw.lines(s, (110, 30, 40), False, [(597, 333), (575, 370), (560, 398)], 5)

        steps = [(480, 515), (520, 500), (565, 488), (605, 474), (650, 463),
                 (695, 452), (740, 443), (785, 435)]
        for i, (x, y) in enumerate(steps):
            w = 18 - i
            pygame.draw.ellipse(s, ORANGE, (x - w // 2, y + (6 if i % 2 else 0), w, w // 2 + 1))

    def draw_office(self, s):
        self.draw_window(s, (80, 110, 180, 170))
        pygame.draw.rect(s, GREY, (80, 110, 180, 170), 6)
        pygame.draw.line(s, GREY, (170, 110), (170, 280), 4)
        pygame.draw.line(s, GREY, (80, 195), (260, 195), 4)
        pygame.draw.polygon(s, (70, 40, 44), [(70, 100), (110, 100), (100, 290), (64, 290)])
        pygame.draw.polygon(s, (70, 40, 44), [(270, 100), (230, 100), (240, 290), (276, 290)])
        pygame.draw.rect(s, (200, 200, 200), (560, 130, 90, 110))
        pygame.draw.rect(s, (110, 112, 118), (568, 138, 74, 94))
        pygame.draw.circle(s, (30, 30, 34), (605, 170), 18)
        pygame.draw.circle(s, (70, 70, 76), (605, 175), 13)
        pygame.draw.line(s, RED, (600, 182), (610, 182), 3)
        pygame.draw.rect(s, (30, 30, 34), (585, 192, 40, 40))
        pygame.draw.rect(s, (60, 62, 68), (690, 320, 100, 110))
        pygame.draw.rect(s, (30, 31, 35), (700, 330, 80, 90))
        for i in range(4):
            pygame.draw.rect(s, PAPER, (708 + i * 3, 395 - i * 8, 60, 6))
        pygame.draw.rect(s, (80, 82, 88), (690, 320, 100, 110), 3)
        pygame.draw.rect(s, (50, 40, 32), (290, 380, 30, 50))
        for a in (-0.7, -0.3, 0.1, 0.5, 0.9):
            pygame.draw.line(s, (60, 70, 60), (305, 380),
                             (305 + 40 * math.sin(a), 380 - 50 * math.cos(a)), 4)
        draw_wall_lamp(s, 470, 200)
        # desk with the insurance contract (Weber stands behind it)
        pygame.draw.rect(s, WOOD, (330, 360, 340, 100))
        pygame.draw.rect(s, (80, 64, 48), (320, 352, 360, 14))
        pygame.draw.rect(s, WOOD_DARK, (340, 375, 120, 70), 2)
        pygame.draw.circle(s, LIGHT_GREY, (400, 410), 4)
        pygame.draw.polygon(s, PAPER, [(500, 352), (580, 346), (585, 360), (505, 366)])
        pygame.draw.polygon(s, PAPER, [(505, 350), (575, 340), (580, 354), (510, 362)])
        pygame.draw.circle(s, RED, (560, 350), 5)
        pygame.draw.rect(s, (40, 60, 50), (620, 330, 10, 24))
        pygame.draw.polygon(s, (90, 120, 100), [(608, 330), (642, 330), (634, 316), (616, 316)])
        glow(s, (625, 330), 30, YELLOW, 60)

    def draw_storage(self, s):
        pygame.draw.line(s, BLACK, (480, TOP_BAR), (480, 80), 2)
        pygame.draw.circle(s, YELLOW, (480, 86), 8)
        alpha_polygon(s, YELLOW, 28, [(474, 90), (486, 90), (700, 430), (260, 430)])
        glow(s, (480, 86), 60, YELLOW, 90)
        pygame.draw.rect(s, WOOD, (560, 150, 220, 8))
        for i, c in enumerate(((120, 120, 120), (100, 100, 104), (140, 136, 130))):
            pygame.draw.rect(s, c, (575 + i * 60, 118, 36, 32))
        # hidden painting behind the crates
        pygame.draw.polygon(s, (90, 90, 96), [(695, 240), (785, 230), (790, 330), (690, 335)])
        pygame.draw.line(s, (70, 70, 76), (700, 260), (780, 300), 3)
        pygame.draw.polygon(s, GOLD, [(785, 230), (765, 232), (787, 252)])
        for rect in ((640, 320, 110, 110), (745, 330, 90, 100), (300, 350, 140, 80)):
            draw_crate(s, rect)
        # coffee cup with lipstick
        pygame.draw.polygon(s, (230, 230, 230), [(354, 320), (378, 320), (375, 348), (357, 348)])
        pygame.draw.arc(s, (230, 230, 230), (372, 326, 14, 14), -1.6, 1.6, 3)
        pygame.draw.line(s, RED, (357, 321), (366, 321), 3)
        for i in range(2):
            ox = 361 + i * 9
            pygame.draw.line(s, GREY, (ox, 314), (ox + math.sin(self.t * 2 + i) * 3, 302), 2)
        # mop, bucket and boots
        pygame.draw.line(s, (120, 100, 80), (205, 295), (215, 420), 5)
        pygame.draw.polygon(s, (130, 130, 130), [(198, 410), (230, 410), (240, 432), (190, 432)])
        pygame.draw.polygon(s, (75, 77, 82), [(180, 385), (230, 385), (225, 432), (185, 432)])
        pygame.draw.ellipse(s, (60, 70, 90), (184, 380, 42, 10))
        for bx in (252, 288):
            pygame.draw.ellipse(s, BLACK, (bx, 413, 34, 18))
            pygame.draw.rect(s, BLACK, (bx + 2, 396, 18, 25))

    # ---- Case 2 rooms -----------------------------------------------------

    def draw_lobby(self, s):
        draw_chandelier(s, 480, 95)
        for x in (110, 850):
            draw_wall_lamp(s, x, 180)
        # portrait of the founder
        pygame.draw.rect(s, (100, 96, 90), (180, 110, 110, 130))
        pygame.draw.circle(s, (130, 126, 120), (235, 160), 22)
        pygame.draw.rect(s, (80, 76, 70), (210, 190, 50, 50))
        pygame.draw.rect(s, GOLD, (180, 110, 110, 130), 6)
        # key rack
        pygame.draw.rect(s, WOOD, (555, 175, 130, 80))
        pygame.draw.rect(s, WOOD_DARK, (555, 175, 130, 80), 3)
        for i in range(5):
            kx = 575 + i * 22
            pygame.draw.line(s, LIGHT_GREY, (kx, 190), (kx, 205), 2)
            pygame.draw.circle(s, LIGHT_GREY, (kx, 212), 6, 2)
            pygame.draw.rect(s, LIGHT_GREY, (kx - 1, 217, 3, 14))
        draw_text(s, "KEYS", self.font_tiny, LIGHT_GREY, (620, 244), center=True)
        # reception desk (Finch stands behind it)
        pygame.draw.rect(s, WOOD, (330, 352, 300, 78))
        pygame.draw.rect(s, (80, 64, 48), (320, 344, 320, 14))
        pygame.draw.line(s, GOLD, (320, 358), (640, 358), 2)
        for px in (370, 450, 530):
            pygame.draw.rect(s, WOOD_DARK, (px, 368, 60, 50), 2)
        pygame.draw.circle(s, GOLD, (365, 338), 9)
        pygame.draw.rect(s, GOLD, (354, 338, 22, 5))
        # the key log book
        pygame.draw.polygon(s, PAPER, [(520, 344), (558, 330), (596, 344), (558, 350)])
        pygame.draw.line(s, INK, (558, 330), (558, 350), 1)
        for i in range(3):
            pygame.draw.line(s, (150, 140, 120), (530 + i * 6, 342 - i * 2), (550, 335 - i * 2), 1)
        # vase of lilies
        pygame.draw.rect(s, (180, 180, 186), (600, 318, 16, 26))
        for a in (-0.5, 0, 0.5):
            end = (608 + 22 * math.sin(a), 318 - 25 * math.cos(a))
            pygame.draw.line(s, (70, 90, 70), (608, 318), end, 2)
            pygame.draw.circle(s, (230, 230, 230), (int(end[0]), int(end[1])), 5)
        # potted palms
        for px in (300, 700):
            pygame.draw.polygon(s, (90, 60, 40), [(px - 18, 430), (px + 18, 430), (px + 14, 400), (px - 14, 400)])
            for a in (-1.0, -0.5, 0, 0.5, 1.0):
                pygame.draw.line(s, (50, 75, 55), (px, 400), (px + 40 * math.sin(a), 400 - 50 * math.cos(a)), 4)

    def draw_ballroom(self, s):
        draw_chandelier(s, 480, 90, lit=False)
        self.draw_window(s, (540, 100, 100, 140))
        pygame.draw.rect(s, GREY, (540, 100, 100, 140), 5)
        pygame.draw.line(s, GREY, (590, 100), (590, 240), 3)
        for cx in (530, 650):
            pygame.draw.polygon(s, (90, 30, 50), [(cx - 6, 92), (cx + 14, 92), (cx + 8, 250), (cx - 10, 250)])
        # grand piano with open lid
        black = (12, 12, 14)
        pygame.draw.polygon(s, black, [(250, 300), (480, 300), (490, 340), (480, 370), (250, 370)])
        pygame.draw.line(s, (60, 60, 70), (252, 302), (478, 302), 2)
        pygame.draw.polygon(s, black, [(300, 300), (470, 300), (430, 220)])
        pygame.draw.line(s, (60, 60, 70), (300, 300), (430, 220), 2)
        pygame.draw.line(s, (60, 60, 66), (430, 220), (420, 300), 2)
        pygame.draw.rect(s, (230, 230, 230), (255, 352, 130, 12))
        for kx in range(258, 385, 9):
            pygame.draw.rect(s, black, (kx + 5, 352, 4, 7))
        for lx in (265, 470):
            pygame.draw.rect(s, black, (lx, 370, 8, 60))
        # tape recorder hidden in the piano
        pygame.draw.rect(s, (60, 60, 66), (385, 292, 48, 22))
        pygame.draw.circle(s, (120, 120, 126), (397, 303), 6, 2)
        pygame.draw.circle(s, (120, 120, 126), (421, 303), 6, 2)
        if int(self.t * 2) % 2 == 0:
            pygame.draw.circle(s, RED, (429, 296), 2)
        pygame.draw.rect(s, PAPER, (300, 330, 40, 22))
        # bench and the broken clasp under it
        pygame.draw.rect(s, black, (290, 400, 110, 16))
        pygame.draw.rect(s, black, (296, 416, 6, 22))
        pygame.draw.rect(s, black, (388, 416, 6, 22))
        pygame.draw.arc(s, (190, 225, 255), (348, 437, 16, 12), 0, 4.5, 2)
        pygame.draw.circle(s, (190, 225, 255), (366, 442), 2)
        # empty display case
        pygame.draw.rect(s, (70, 70, 76), (630, 360, 80, 70))
        pygame.draw.rect(s, (90, 30, 40), (642, 338, 56, 22))
        alpha_polygon(s, (200, 220, 240), 40, [(625, 280), (715, 280), (715, 360), (625, 360)])
        pygame.draw.rect(s, (160, 170, 180), (625, 280, 90, 80), 2)
        pygame.draw.line(s, (160, 170, 180), (625, 280), (600, 262), 2)
        pygame.draw.line(s, (160, 170, 180), (715, 280), (690, 262), 2)
        pygame.draw.line(s, (160, 170, 180), (600, 262), (690, 262), 2)

    def draw_kitchen(self, s):
        for x in range(0, WIDTH, 40):
            pygame.draw.line(s, (70, 72, 70), (x, TOP_BAR + 22), (x, FLOOR_Y - 8), 1)
        for y in range(TOP_BAR + 22, FLOOR_Y - 8, 40):
            pygame.draw.line(s, (70, 72, 70), (0, y), (WIDTH, y), 1)
        # hanging pans
        pygame.draw.line(s, (90, 90, 96), (420, 100), (520, 100), 3)
        for px in (430, 465, 500):
            pygame.draw.line(s, (90, 90, 96), (px, 100), (px, 116), 2)
            pygame.draw.circle(s, (60, 60, 66), (px, 132), 15)
            pygame.draw.circle(s, (80, 80, 86), (px, 132), 15, 2)
        # shelf with egg timers - one is missing
        pygame.draw.rect(s, WOOD, (190, 195, 170, 10))
        for i in range(6):
            tx = 210 + i * 27
            if i == 3:
                pygame.draw.circle(s, (80, 82, 80), (tx, 182), 9, 1)
                continue
            pygame.draw.ellipse(s, (205, 205, 200), (tx - 9, 168, 18, 26))
            pygame.draw.line(s, (90, 90, 90), (tx, 174), (tx, 182), 2)
        # counter with flour bag and glove
        pygame.draw.rect(s, (90, 92, 96), (160, 340, 300, 90))
        pygame.draw.rect(s, (130, 132, 136), (152, 332, 316, 12))
        for dx in (170, 270, 370):
            pygame.draw.rect(s, (80, 82, 86), (dx, 352, 80, 70), 2)
        pygame.draw.polygon(s, (200, 195, 180), [(190, 332), (232, 332), (226, 290), (196, 290)])
        draw_text(s, "FLOUR", self.font_tiny, (110, 100, 80), (211, 314), center=True)
        pygame.draw.ellipse(s, (240, 240, 235), (290, 318, 34, 16))
        for fx in range(292, 300, 3):
            pygame.draw.line(s, (240, 240, 235), (fx + 30, 322), (fx + 38, 314), 4)
        # stove with pots and hood
        pygame.draw.polygon(s, (70, 72, 76), [(540, 140), (720, 140), (690, 200), (570, 200)])
        pygame.draw.rect(s, (50, 51, 55), (555, 315, 150, 115))
        pygame.draw.rect(s, BLACK, (575, 360, 110, 55))
        glow(s, (630, 395), 40, ORANGE, 40)
        for px in (585, 640):
            pygame.draw.rect(s, (120, 122, 126), (px, 285, 45, 32))
            for i in range(2):
                sx = px + 15 + i * 14
                pygame.draw.line(s, GREY, (sx, 280), (sx + math.sin(self.t * 2 + i + px) * 4, 262), 2)
        # rubbish bin with a crumpled letter
        pygame.draw.polygon(s, (80, 82, 86), [(716, 360), (772, 360), (766, 432), (722, 432)])
        pygame.draw.rect(s, (100, 102, 106), (712, 354, 64, 8))
        pygame.draw.circle(s, PAPER, (744, 350), 11)
        pygame.draw.line(s, (180, 170, 150), (736, 346), (750, 354), 1)
        # cake on the floor
        pygame.draw.ellipse(s, (70, 45, 30), (360, 462, 90, 26))
        pygame.draw.ellipse(s, (95, 60, 40), (372, 456, 50, 18))

    def draw_fuseroom(self, s):
        for y in (95, 115):
            pygame.draw.rect(s, (70, 72, 76), (0, y, WIDTH, 10))
            pygame.draw.line(s, (100, 102, 106), (0, y + 2), (WIDTH, y + 2), 1)
        pygame.draw.rect(s, (70, 72, 76), (360, 95, 10, 335))
        pygame.draw.line(s, BLACK, (480, TOP_BAR), (480, 130), 2)
        pygame.draw.circle(s, YELLOW, (480, 136), 6)
        glow(s, (480, 136), 60, YELLOW, 80)
        alpha_polygon(s, YELLOW, 22, [(476, 140), (484, 140), (640, 430), (320, 430)])
        # fuse box with egg timer
        pygame.draw.rect(s, (80, 84, 90), (420, 160, 140, 165))
        pygame.draw.rect(s, (40, 42, 46), (432, 172, 116, 120))
        for row in range(3):
            for col in range(4):
                pygame.draw.rect(s, (150, 150, 150), (442 + col * 27, 182 + row * 35, 12, 22))
        pygame.draw.rect(s, RED, (520, 292, 22, 28))
        pygame.draw.polygon(s, (90, 94, 100), [(420, 160), (380, 175), (380, 340), (420, 325)])
        draw_text(s, "DANGER", self.font_tiny, YELLOW, (490, 310), center=True)
        pygame.draw.ellipse(s, (240, 240, 230), (512, 258, 28, 36))
        pygame.draw.line(s, ORANGE, (526, 266), (526, 278), 2)
        pygame.draw.line(s, ORANGE, (526, 278), (533, 281), 2)
        pygame.draw.lines(s, RED, False, [(540, 280), (555, 290), (535, 306)], 2)
        # sheet music on the floor
        pygame.draw.polygon(s, PAPER, [(590, 470), (655, 460), (665, 488), (598, 496)])
        for i in range(4):
            y = 469 + i * 6
            pygame.draw.line(s, (120, 110, 90), (598, y + 2), (655, y - 6), 1)
        pygame.draw.circle(s, INK, (620, 472), 2)
        pygame.draw.circle(s, INK, (634, 474), 2)
        # boiler
        pygame.draw.rect(s, (70, 64, 58), (700, 190, 100, 240), border_radius=30)
        pygame.draw.line(s, (90, 84, 78), (708, 210), (708, 410), 3)
        pygame.draw.circle(s, (40, 36, 32), (750, 260), 20)
        pygame.draw.circle(s, (180, 180, 180), (750, 260), 16, 2)
        pygame.draw.line(s, RED, (750, 260), (758 + 3 * math.sin(self.t * 5), 250), 2)
        pygame.draw.circle(s, ORANGE if int(self.t * 3) % 2 else (150, 80, 20), (750, 360), 5)

    # ---- Case 3 rooms -----------------------------------------------------

    def draw_dining(self, s):
        self.draw_window(s, (440, 100, 120, 150), lightning=True)
        pygame.draw.rect(s, GREY, (440, 100, 120, 150), 6)
        pygame.draw.line(s, GREY, (500, 100), (500, 250), 3)
        for cx in (420, 566):
            pygame.draw.polygon(s, (90, 26, 30), [(cx, 90), (cx + 16, 90), (cx + 20, 270), (cx - 4, 270)])
        # portrait of the professor
        pygame.draw.rect(s, (100, 96, 90), (300, 105, 100, 130))
        pygame.draw.circle(s, (40, 40, 44), (350, 160), 22)
        pygame.draw.circle(s, (130, 126, 120), (350, 165), 16)
        pygame.draw.circle(s, (60, 60, 66), (344, 165), 5, 1)
        pygame.draw.circle(s, (60, 60, 66), (356, 165), 5, 1)
        pygame.draw.rect(s, (60, 58, 56), (325, 190, 50, 45))
        pygame.draw.rect(s, GOLD, (300, 105, 100, 130), 6)
        draw_chandelier(s, 260, 110)
        # sideboard with the butler's notes
        pygame.draw.rect(s, WOOD, (590, 270, 160, 85))
        pygame.draw.rect(s, WOOD_DARK, (590, 270, 160, 85), 3)
        pygame.draw.line(s, WOOD_DARK, (670, 270), (670, 355), 2)
        pygame.draw.polygon(s, PAPER, [(625, 262), (685, 256), (690, 268), (630, 272)])
        for i in range(3):
            pygame.draw.line(s, (150, 140, 120), (632, 269 - i * 2), (680, 264 - i * 2), 1)
        pygame.draw.rect(s, (200, 200, 205), (710, 240, 14, 30))
        # long dinner table
        pygame.draw.rect(s, (225, 222, 215), (180, 358, 600, 20))
        pygame.draw.rect(s, WOOD, (180, 378, 600, 55))
        for k in range(8):
            pygame.draw.line(s, (205, 202, 195), (190 + k * 75, 378), (196 + k * 75, 392), 2)
        for px in range(215, 780, 85):
            pygame.draw.ellipse(s, (245, 245, 245), (px - 18, 350, 36, 12))
            pygame.draw.ellipse(s, (210, 210, 210), (px - 10, 352, 20, 7), 1)
        for cx in (300, 480, 660):
            pygame.draw.rect(s, (230, 230, 220), (cx - 3, 325, 6, 28))
            pygame.draw.circle(s, YELLOW, (cx, 321 + int(math.sin(self.t * 8 + cx))), 4)
            glow(s, (cx, 321), 28, YELLOW, 80)
        # ashtray with a cigar
        pygame.draw.ellipse(s, (120, 120, 126), (630, 345, 40, 12))
        pygame.draw.line(s, (120, 90, 60), (640, 347), (665, 342), 4)
        pygame.draw.line(s, (130, 130, 130), (666, 340), (668 + math.sin(self.t * 2) * 3, 322), 1)

    def draw_library(self, s):
        draw_shelf_of_books(s, (160, 90, 190, 330), 1)
        if "passage" in self.found:
            pygame.draw.rect(s, BLACK, (590, 90, 120, 330))
            draw_shelf_of_books(s, (690, 90, 190, 330), 2)
        else:
            draw_shelf_of_books(s, (590, 90, 190, 330), 2)
            pygame.draw.circle(s, (110, 90, 60), (600, 260), 3)
        # fireplace with a half-burnt telegram
        pygame.draw.rect(s, (90, 88, 86), (370, 250, 150, 180))
        for y in range(262, 430, 16):
            pygame.draw.line(s, (78, 76, 74), (370, y), (520, y), 1)
        pygame.draw.rect(s, (110, 108, 104), (360, 240, 170, 16))
        pygame.draw.rect(s, BLACK, (395, 300, 100, 130))
        for i in range(3):
            fx = 420 + i * 22
            h = 26 + 8 * math.sin(self.t * 6 + i * 2)
            pygame.draw.polygon(s, ORANGE, [(fx - 9, 430), (fx + 9, 430), (fx, 430 - h)])
            pygame.draw.polygon(s, YELLOW, [(fx - 4, 430), (fx + 4, 430), (fx, 430 - h * 0.5)])
        glow(s, (445, 410), 70, ORANGE, 80)
        pygame.draw.polygon(s, PAPER, [(440, 410), (500, 404), (505, 424), (446, 428)])
        pygame.draw.polygon(s, (40, 30, 20), [(440, 410), (458, 408), (450, 428), (446, 428)])
        pygame.draw.rect(s, GOLD, (400, 222, 14, 18))
        pygame.draw.rect(s, (200, 200, 205), (470, 226, 8, 14))
        # side table with Lily's camera
        pygame.draw.rect(s, WOOD, (530, 385, 50, 8))
        pygame.draw.rect(s, WOOD_DARK, (550, 393, 8, 37))
        pygame.draw.rect(s, (40, 40, 46), (532, 364, 40, 22), border_radius=3)
        pygame.draw.circle(s, (110, 180, 210), (552, 375), 7, 2)

    def draw_lab(self, s):
        for x in range(60, WIDTH, 220):
            pygame.draw.rect(s, (210, 220, 230), (x, TOP_BAR + 6, 120, 8))
            alpha_polygon(s, (220, 235, 255), 18, [(x, TOP_BAR + 14), (x + 120, TOP_BAR + 14),
                                                    (x + 170, 430), (x - 50, 430)])
        # blackboard
        pygame.draw.rect(s, (30, 44, 36), (300, 105, 260, 135))
        pygame.draw.rect(s, WOOD, (300, 105, 260, 135), 6)
        for i, line in enumerate(["E = U * I * t", "Li + C6 -> LiC6", "10x STRONGER!", "  ???"]):
            draw_text(s, line, self.font_small, (200, 205, 200), (320, 118 + i * 26))
        # lab bench with flasks
        pygame.draw.rect(s, (70, 72, 76), (150, 350, 300, 80))
        pygame.draw.rect(s, (110, 112, 116), (142, 342, 316, 12))
        for fx, liquid in ((190, (120, 150, 130)), (240, (140, 120, 150)), (300, (150, 150, 120))):
            pygame.draw.polygon(s, liquid, [(fx - 10, 324), (fx + 10, 324), (fx + 15, 340), (fx - 15, 340)])
            pygame.draw.polygon(s, (200, 205, 210), [(fx - 4, 300), (fx + 4, 300),
                                                     (fx + 16, 342), (fx - 16, 342)], 2)
            for b in range(2):
                by = 336 - (self.t * 20 + b * 7 + fx) % 14
                pygame.draw.circle(s, shade(liquid, 50), (fx - 3 + b * 6, int(by)), 2)
        pygame.draw.ellipse(s, (180, 160, 120), (370, 330, 40, 14))
        # open safe
        pygame.draw.rect(s, (70, 74, 80), (620, 250, 125, 145))
        pygame.draw.rect(s, BLACK, (632, 262, 101, 121))
        pygame.draw.polygon(s, (90, 94, 100), [(620, 250), (585, 262), (585, 400), (620, 395)])
        pygame.draw.circle(s, LIGHT_GREY, (602, 320), 10, 2)
        pygame.draw.rect(s, (60, 62, 68), (640, 395, 85, 35))
        # hairpin and cigar ash on the floor
        pygame.draw.line(s, (220, 190, 90), (596, 452), (636, 446), 2)
        pygame.draw.line(s, (220, 190, 90), (596, 452), (632, 455), 2)
        pygame.draw.circle(s, (220, 190, 90), (596, 452), 3)
        pygame.draw.ellipse(s, (140, 140, 140), (690, 450, 38, 12))
        pygame.draw.ellipse(s, (170, 170, 170), (700, 448, 18, 7))
        # strange machine
        pygame.draw.rect(s, (60, 62, 68), (800, 360, 90, 70))
        for i in range(3):
            pygame.draw.circle(s, GREEN_LIGHT if int(self.t * 3 + i) % 2 else (40, 60, 40), (820 + i * 22, 385), 5)
        pygame.draw.rect(s, (130, 90, 50), (835, 200, 20, 160))
        for y in range(210, 355, 12):
            pygame.draw.ellipse(s, (170, 110, 60), (825, y, 40, 8), 2)
        pygame.draw.circle(s, (150, 150, 160), (845, 190), 18)
        if int(self.t * 4) % 3 == 0:
            pygame.draw.lines(s, (180, 200, 255), False, [(860, 185), (875, 175), (870, 165), (888, 155)], 2)
            glow(s, (875, 170), 30, (180, 200, 255), 80)

    def draw_greenhouse(self, s):
        self.draw_window(s, (0, TOP_BAR, WIDTH, FLOOR_Y - TOP_BAR - 8), lightning=True)
        for x in range(0, WIDTH, 120):
            pygame.draw.line(s, (150, 160, 160), (x, TOP_BAR), (x, FLOOR_Y), 4)
        for y in (TOP_BAR + 100, TOP_BAR + 230):
            pygame.draw.line(s, (150, 160, 160), (0, y), (WIDTH, y), 4)
        # hanging plants
        for hx in (240, 520):
            pygame.draw.line(s, (60, 60, 60), (hx, TOP_BAR), (hx, 110), 2)
            pygame.draw.ellipse(s, (120, 70, 50), (hx - 18, 108, 36, 20))
            for k in range(5):
                pygame.draw.line(s, (60, 90, 60), (hx - 12 + k * 6, 120), (hx - 20 + k * 10, 160 + k % 2 * 14), 2)
        # flower pots on a bench
        pygame.draw.rect(s, WOOD, (160, 380, 220, 12))
        for leg in (170, 360):
            pygame.draw.rect(s, WOOD_DARK, (leg, 392, 8, 38))
        for i, px in enumerate((185, 240, 295, 345)):
            pygame.draw.polygon(s, (120, 70, 50), [(px - 16, 350), (px + 16, 350), (px + 12, 380), (px - 12, 380)])
            for a in (-0.6, 0, 0.6):
                pygame.draw.line(s, (60, 85, 60), (px, 350), (px + 25 * math.sin(a + i), 350 - 35 * math.cos(a)), 3)
            pygame.draw.circle(s, (200, 120, 160), (px + 6, 318), 4)
        # hidden coat behind the palm
        pygame.draw.polygon(s, (92, 76, 60), [(670, 300), (720, 300), (730, 400), (660, 400)])
        pygame.draw.polygon(s, (120, 100, 80), [(670, 300), (695, 330), (720, 300)])
        for by in (340, 360, 380):
            pygame.draw.circle(s, (40, 32, 26), (695, by), 3)
        pygame.draw.rect(s, PAPER, (704, 352, 14, 8))
        # big palm tree
        pygame.draw.polygon(s, (120, 70, 50), [(640, 430), (720, 430), (705, 390), (655, 390)])
        pygame.draw.line(s, (90, 70, 50), (680, 390), (690, 200), 9)
        for a in (-2.4, -1.9, -1.2, -0.6, 0.0, 0.6):
            end = (690 + 95 * math.cos(a), 200 + 70 * math.sin(a) + 40)
            pygame.draw.line(s, (50, 75, 55), (690, 200), end, 7)

    # ---- Case 4 rooms (train) ---------------------------------------------

    def draw_train_windows(self, s, xs, width=120):
        for x in xs:
            frame = pygame.Rect(x - 6, 104, width + 12, 132)
            pygame.draw.rect(s, BRASS, frame, border_radius=16)
            pane = pygame.Rect(x, 110, width, 120)
            self.draw_window(s, pane, mountains=True)
            pygame.draw.rect(s, shade(BRASS, -40), pane, 2, border_radius=12)
            pygame.draw.polygon(s, (215, 220, 232), [pane.bottomleft, (pane.x + 26, pane.bottom), (pane.x, pane.bottom - 16)])
            pygame.draw.polygon(s, (215, 220, 232), [pane.bottomright, (pane.right - 22, pane.bottom), (pane.right, pane.bottom - 12)])
            for cx, side in ((x - 4, -1), (x + width + 4, 1)):
                pygame.draw.polygon(s, (110, 40, 46), [(cx, 100), (cx + 14 * side, 100), (cx + 18 * side, 250), (cx - 2 * side, 250)])
        for x in xs[1:]:
            draw_wall_lamp(s, x - 30, 160)

    def draw_lounge(self, s):
        self.draw_train_windows(s, [245], width=170)
        # bar with bottles
        pygame.draw.rect(s, WOOD_DARK, (600, 140, 200, 120))
        for row, y in enumerate((180, 228)):
            pygame.draw.rect(s, BRASS, (600, y, 200, 4))
            for k in range(8):
                bx = 610 + k * 23
                tone = (60 + (k * 37 + row * 11) % 90, 80, 70 + (k * 23) % 80)
                pygame.draw.rect(s, tone, (bx, y - 30, 12, 30), border_radius=3)
                pygame.draw.rect(s, tone, (bx + 4, y - 38, 4, 10))
                pygame.draw.line(s, shade(tone, 50), (bx + 2, y - 26), (bx + 2, y - 6), 1)
        pygame.draw.rect(s, WOOD, (600, 310, 200, 120))
        pygame.draw.rect(s, (90, 64, 44), (590, 300, 220, 14))
        pygame.draw.line(s, BRASS, (600, 420), (800, 420), 3)
        # gramophone
        pygame.draw.rect(s, WOOD_DARK, (700, 280, 50, 22))
        pygame.draw.line(s, BRASS, (725, 280), (730, 262), 3)
        pygame.draw.polygon(s, BRASS, [(728, 266), (765, 236), (775, 256)])
        pygame.draw.ellipse(s, (20, 20, 22), (704, 276, 36, 8))
        # armchair with the telegram
        pygame.draw.rect(s, (90, 40, 46), (180, 360, 110, 70), border_radius=12)
        pygame.draw.rect(s, (110, 50, 56), (190, 340, 90, 40), border_radius=10)
        pygame.draw.rect(s, (80, 34, 40), (172, 360, 22, 60), border_radius=8)
        pygame.draw.rect(s, (80, 34, 40), (276, 360, 22, 60), border_radius=8)
        pygame.draw.polygon(s, PAPER, [(215, 362), (258, 356), (262, 372), (220, 378)])
        # small table with program and champagne
        pygame.draw.ellipse(s, WOOD, (345, 388, 90, 20))
        pygame.draw.rect(s, WOOD_DARK, (386, 398, 8, 32))
        pygame.draw.polygon(s, PAPER, [(360, 384), (400, 378), (416, 390), (372, 396)])
        pygame.draw.circle(s, RED, (392, 386), 3)
        pygame.draw.line(s, (220, 220, 230), (418, 390), (418, 368), 1)
        pygame.draw.polygon(s, (220, 220, 230), [(412, 368), (424, 368), (418, 358)], 1)

    def draw_train_dining(self, s):
        self.draw_train_windows(s, [200, 420, 640])
        for tx in (180, 400):
            pygame.draw.rect(s, (225, 222, 215), (tx, 330, 160, 22))
            pygame.draw.polygon(s, (205, 202, 195), [(tx, 352), (tx + 160, 352), (tx + 154, 380), (tx + 6, 380)])
            pygame.draw.rect(s, WOOD_DARK, (tx + 70, 380, 20, 50))
            pygame.draw.ellipse(s, WHITE, (tx + 20, 322, 34, 10))
            pygame.draw.ellipse(s, WHITE, (tx + 106, 322, 34, 10))
            pygame.draw.rect(s, BRASS, (tx + 76, 300, 6, 24))
            pygame.draw.polygon(s, (170, 50, 50), [(tx + 64, 300), (tx + 94, 300), (tx + 86, 286), (tx + 72, 286)])
            glow(s, (tx + 79, 300), 40, (255, 180, 120), 70)
        # chess board on table 2
        for row in range(3):
            for col in range(8):
                color = (230, 230, 230) if (row + col) % 2 == 0 else (40, 40, 44)
                pygame.draw.rect(s, color, (432 + col * 9, 322 + row * 6, 9, 6))
        pygame.draw.circle(s, WHITE, (450, 316), 3)
        pygame.draw.circle(s, BLACK, (470, 316), 3)
        # serving cart with order slips
        pygame.draw.rect(s, (130, 132, 140), (650, 350, 120, 8))
        pygame.draw.rect(s, (130, 132, 140), (650, 400, 120, 6))
        for lx in (655, 760):
            pygame.draw.line(s, (130, 132, 140), (lx, 350), (lx, 420), 3)
            pygame.draw.circle(s, BLACK, (lx, 424), 6)
        pygame.draw.ellipse(s, (200, 200, 205), (720, 330, 34, 22))
        pygame.draw.line(s, (200, 200, 205), (752, 336), (762, 330), 3)
        pygame.draw.line(s, (90, 90, 96), (700, 348), (700, 322), 2)
        for k in range(3):
            pygame.draw.rect(s, PAPER, (686 + k * 3, 326 + k * 6, 26, 10))

    def draw_sleeper(self, s):
        for i, x in enumerate((165, 305, 445, 585)):
            open_door = i in (1, 3)
            pygame.draw.rect(s, (40, 30, 24), (x, 200, 120, 230))
            if open_door:
                pygame.draw.rect(s, (90, 60, 50), (x + 6, 206, 108, 224))
                pygame.draw.rect(s, (130, 40, 46), (x + 10, 330, 100, 40))
                pygame.draw.rect(s, WHITE, (x + 14, 316, 30, 16), border_radius=4)
                self.draw_window(s, (x + 30, 230, 60, 60))
                glow(s, (x + 60, 300), 60, YELLOW, 40)
            else:
                pygame.draw.rect(s, (82, 58, 42), (x + 6, 206, 108, 224))
                pygame.draw.rect(s, (30, 40, 60), (x + 26, 222, 68, 80), border_radius=6)
                pygame.draw.rect(s, BRASS, (x + 26, 222, 68, 80), 2, border_radius=6)
                pygame.draw.rect(s, BRASS, (x + 96, 320, 5, 34), border_radius=2)
            pygame.draw.rect(s, BRASS, (x, 200, 120, 230), 3)
            pygame.draw.rect(s, BRASS, (x + 45, 180, 30, 16))
            draw_text(s, str(i + 1), self.font_small_bold, BLACK, (x + 60, 188), center=True)
        # doctor's bag in compartment 2
        pygame.draw.rect(s, (40, 30, 26), (334, 330, 56, 30), border_radius=6)
        pygame.draw.arc(s, BRASS, (348, 318, 28, 20), 0, math.pi, 3)
        pygame.draw.line(s, BRASS, (334, 340), (390, 340), 2)
        # hatbox in compartment 4
        pygame.draw.ellipse(s, (200, 160, 170), (612, 346, 66, 20))
        pygame.draw.rect(s, (200, 160, 170), (612, 322, 66, 34))
        pygame.draw.ellipse(s, (220, 185, 195), (612, 314, 66, 18))
        pygame.draw.rect(s, BRASS, (638, 336, 14, 12))
        if "egg" in self.found:
            glow(s, (645, 322), 30, GOLD, 90)
        # wet heel prints from the luggage car to compartment 4
        for k in range(7):
            hx = 800 - k * 24
            hy = 448 + (6 if k % 2 else 0)
            alpha_ellipse(s, (140, 170, 210), 120, (hx - 7, hy, 14, 7))
            alpha_ellipse(s, (140, 170, 210), 120, (hx + 9, hy + 2, 4, 4))

    def draw_luggage(self, s):
        # single swinging lamp
        swing = math.sin(self.t * 1.3) * 12
        pygame.draw.line(s, BLACK, (480, TOP_BAR), (480 + swing, 92), 2)
        pygame.draw.circle(s, YELLOW, (int(480 + swing), 96), 7)
        glow(s, (480 + swing, 96), 70, YELLOW, 90)
        alpha_polygon(s, YELLOW, 22, [(476 + swing, 100), (484 + swing, 100), (700, 430), (260, 430)])
        # suitcases and crates
        draw_crate(s, (60, 340, 90, 90))
        draw_suitcase(s, (760, 380, 120, 50), (90, 60, 50))
        draw_suitcase(s, (770, 340, 100, 40), (60, 70, 90))
        draw_suitcase(s, (250, 400, 70, 30), (80, 70, 60))
        # open window with snow blowing in
        self.draw_window(s, (760, 100, 130, 100))
        pygame.draw.rect(s, (80, 84, 90), (760, 100, 130, 100), 5)
        pygame.draw.polygon(s, (90, 94, 100), [(760, 100), (720, 120), (720, 220), (760, 200)])
        for k in range(8):
            fx = 760 - (self.t * 60 + k * 40) % 260
            fy = 140 + k * 8 + 20 * math.sin(self.t * 2 + k)
            pygame.draw.circle(s, (235, 238, 245), (int(fx), int(fy)), 2)
        pygame.draw.polygon(s, (215, 220, 232), [(700, 430), (790, 430), (770, 418), (730, 414)])
        # cage with an empty stand inside
        pygame.draw.rect(s, (40, 30, 26), (440, 330, 100, 100))
        pygame.draw.rect(s, (110, 30, 40), (450, 310, 80, 24))
        pygame.draw.ellipse(s, (130, 40, 50), (462, 300, 56, 16))
        for x in range(300, 640, 20):
            pygame.draw.line(s, (120, 124, 130), (x, 140), (x, 430), 3)
        pygame.draw.line(s, (120, 124, 130), (300, 140), (640, 140), 4)
        pygame.draw.line(s, (120, 124, 130), (300, 300), (640, 300), 2)
        # cage door, swung open
        for k in range(5):
            x = 645 + k * 18
            pygame.draw.line(s, (140, 144, 150), (x, 150 + k * 4), (x, 420 - k * 4), 3)
        pygame.draw.line(s, (140, 144, 150), (645, 150), (717, 166), 3)
        pygame.draw.line(s, (140, 144, 150), (645, 420), (717, 404), 3)
        pygame.draw.rect(s, BRASS, (700, 270, 14, 20))
        # white feather stuck in the door
        pygame.draw.line(s, (235, 235, 235), (684, 270), (708, 246), 2)
        for k in range(6):
            fx = 686 + k * 4
            fy = 268 - k * 4
            pygame.draw.line(s, (235, 235, 235), (fx, fy), (fx - 6, fy - 6), 1)
            pygame.draw.line(s, (235, 235, 235), (fx, fy), (fx + 6, fy + 2), 1)
        # sleeping guard on a chair with a cup next to him
        pygame.draw.rect(s, WOOD_DARK, (180, 380, 70, 8))
        for lx in (184, 240):
            pygame.draw.line(s, WOOD_DARK, (lx, 388), (lx, 430), 4)
        pygame.draw.rect(s, WOOD_DARK, (236, 320, 8, 64))
        pygame.draw.polygon(s, (20, 20, 24), [(190, 382), (240, 382), (232, 322), (198, 326)])
        pygame.draw.rect(s, (20, 20, 24), (196, 386, 14, 40))
        pygame.draw.rect(s, (20, 20, 24), (220, 386, 14, 40))
        pygame.draw.circle(s, (62, 62, 68), (205, 316), 15)
        pygame.draw.rect(s, (20, 20, 24), (190, 296, 32, 10))
        z = int(self.t * 1.5) % 3
        for k in range(z + 1):
            draw_text(s, "z", self.font_bold, LIGHT_GREY, (170 - k * 12, 290 - k * 16))
        draw_crate(s, (262, 396, 48, 34))
        pygame.draw.polygon(s, (220, 220, 220), [(272, 378), (294, 378), (291, 396), (275, 396)])
        pygame.draw.arc(s, (220, 220, 220), (289, 382, 12, 10), -1.6, 1.6, 2)
        pygame.draw.ellipse(s, (110, 70, 50), (274, 377, 18, 4))

    # ---- Case 5 rooms (circus) --------------------------------------------

    def draw_bigtop(self, s):
        # coloured spotlights
        alpha_polygon(s, (255, 220, 120), 30, [(120, TOP_BAR), (150, TOP_BAR), (520, 520), (380, 520)])
        alpha_polygon(s, (255, 120, 200), 26, [(820, TOP_BAR), (850, TOP_BAR), (580, 520), (440, 520)])
        pygame.draw.line(s, (60, 40, 30), (480, TOP_BAR), (480, 70), 8)
        # ring
        pygame.draw.ellipse(s, (120, 30, 40), (210, 440, 540, 120))
        pygame.draw.ellipse(s, (104, 84, 60), (226, 450, 508, 100))
        pygame.draw.ellipse(s, GOLD, (210, 440, 540, 120), 2)
        for k in range(16):
            a = k * math.pi / 8
            pygame.draw.circle(s, (230, 216, 196), (int(480 + 262 * math.cos(a)), int(500 + 57 * math.sin(a))), 3)
        # trapeze with one snapped rope
        pygame.draw.line(s, (200, 190, 170), (430, TOP_BAR), (430, 160), 2)
        pygame.draw.line(s, (200, 190, 170), (540, TOP_BAR), (540, 110), 2)
        for k in range(4):
            pygame.draw.line(s, (200, 190, 170), (540, 110), (536 + k * 3, 120 + k % 2 * 4), 1)
        sway = math.sin(self.t * 1.5) * 4
        pygame.draw.line(s, (180, 180, 186), (430, 160), (450 + sway, 230), 5)
        # safety net
        net = [(330, 300), (630, 300), (610, 345), (350, 345)]
        pygame.draw.polygon(s, (40, 30, 34), net)
        for k in range(16):
            x = 330 + k * 20
            pygame.draw.line(s, (180, 170, 150), (x, 300), (x - 20 + k * 2.5, 345), 1)
            pygame.draw.line(s, (180, 170, 150), (x, 300), (x + 20 - k * 2.5, 345), 1)
        pygame.draw.polygon(s, (200, 190, 170), net, 2)
        for px in (340, 620):
            pygame.draw.line(s, (110, 110, 116), (px, 300), (px, 440), 3)
        # rope ladder with a white smudge
        for lx in (670, 700):
            pygame.draw.line(s, (180, 160, 120), (lx, TOP_BAR), (lx + 6, 430), 2)
        for y in range(80, 430, 22):
            pygame.draw.line(s, (180, 160, 120), (670 + (y - 50) * 0.016, y), (700 + (y - 50) * 0.016, y), 3)
        pygame.draw.ellipse(s, (240, 240, 240), (676, 250, 16, 8))
        pygame.draw.circle(s, (240, 240, 240), (690, 258), 3)
        # bleachers with seat A1
        for row in range(3):
            y = 340 + row * 28
            pygame.draw.rect(s, (60, 26, 34), (160, y, 140, 24))
            pygame.draw.line(s, GOLD, (160, y), (300, y), 1)
            for k in range(6):
                pygame.draw.circle(s, (20, 14, 20), (172 + k * 23, y - 4), 7)
        draw_text(s, "A1", self.font_tiny, GOLD, (176, 404), center=True)
        pygame.draw.rect(s, PAPER, (196, 378, 30, 14))
        pygame.draw.rect(s, RED, (196, 378, 6, 14))
        for k in range(6):
            pygame.draw.circle(s, (240, 230, 190), (250 + k * 9, 420 + (k * 7) % 10), 2)

    def draw_backstage(self, s):
        # mirror with light bulbs
        pygame.draw.rect(s, WOOD_DARK, (250, 110, 170, 130))
        pygame.draw.rect(s, (130, 140, 150), (262, 122, 146, 106))
        alpha_polygon(s, WHITE, 30, [(262, 122), (330, 122), (262, 200)])
        draw_text(s, "A1 - after the show - 5000", self.font_tiny, (245, 245, 245), (335, 190), center=True)
        for k in range(6):
            for bx, by in ((256 + k * 31, 114), (256 + k * 31, 236)):
                pygame.draw.circle(s, YELLOW, (bx, by), 5)
        glow(s, (335, 175), 110, YELLOW, 50)
        # make-up table
        pygame.draw.rect(s, WOOD, (230, 300, 210, 14))
        pygame.draw.rect(s, WOOD_DARK, (240, 314, 10, 116))
        pygame.draw.rect(s, WOOD_DARK, (420, 314, 10, 116))
        for k, c in enumerate(((240, 240, 240), (220, 60, 60), (60, 120, 220), (240, 200, 60))):
            pygame.draw.rect(s, c, (250 + k * 22, 286, 14, 14), border_radius=3)
        pygame.draw.circle(s, RED, (350, 292), 7)
        # Igor's knife
        pygame.draw.polygon(s, (200, 205, 210), [(384, 296), (412, 290), (414, 294), (386, 300)])
        pygame.draw.rect(s, (90, 60, 40), (412, 289, 14, 7), border_radius=2)
        # costume rack
        pygame.draw.line(s, (120, 120, 126), (480, 140), (620, 140), 4)
        for lx in (484, 616):
            pygame.draw.line(s, (120, 120, 126), (lx, 140), (lx, 430), 3)
        for k, c in enumerate(((150, 40, 60), (60, 90, 150), (200, 170, 60), (90, 140, 90), (180, 90, 160))):
            x = 494 + k * 25
            pygame.draw.polygon(s, c, [(x, 146), (x + 22, 146), (x + 28, 300), (x - 6, 300)])
            pygame.draw.line(s, shade(c, 40), (x + 4, 150), (x + 2, 296), 1)
        # lockers 5, 6, 7
        for i, x in enumerate((640, 694, 748)):
            pygame.draw.rect(s, (80, 92, 100), (x, 160, 54, 270))
            pygame.draw.rect(s, (60, 70, 76), (x, 160, 54, 270), 3)
            for v in range(4):
                pygame.draw.line(s, (50, 58, 64), (x + 14, 180 + v * 8), (x + 40, 180 + v * 8), 2)
            pygame.draw.rect(s, (200, 200, 205), (x + 18, 220, 18, 12))
            draw_text(s, str(5 + i), self.font_tiny, BLACK, (x + 27, 226), center=True)
            pygame.draw.rect(s, (150, 150, 156), (x + 40, 290, 6, 20))
        pygame.draw.circle(s, RED, (775, 260), 6)
        if "locker" in self.found:
            pygame.draw.rect(s, BLACK, (752, 164, 46, 262))
            pygame.draw.rect(s, PAPER, (762, 300, 28, 18))

    def draw_fortune(self, s):
        for lx in (300, 660):
            pygame.draw.line(s, (60, 50, 40), (lx, TOP_BAR), (lx, 120), 2)
            pygame.draw.rect(s, (120, 80, 40), (lx - 12, 120, 24, 30), border_radius=6)
            pygame.draw.rect(s, (255, 190, 100), (lx - 8, 124, 16, 22), border_radius=4)
            glow(s, (lx, 135), 70, (255, 170, 80), 80)
        # poster
        pygame.draw.rect(s, (200, 180, 130), (180, 115, 120, 160))
        pygame.draw.rect(s, (90, 40, 90), (180, 115, 120, 160), 4)
        draw_text(s, "MADAME", self.font_small_bold, (90, 30, 90), (240, 135), center=True)
        draw_text(s, "ZORA", self.font_big, (90, 30, 90), (240, 162), center=True)
        pygame.draw.circle(s, (90, 30, 90), (240, 210), 22, 3)
        for k in range(5):
            a = -math.pi / 2 + k * 2 * math.pi / 5
            pygame.draw.circle(s, GOLD, (int(240 + 30 * math.cos(a)), int(210 + 30 * math.sin(a))), 3)
        draw_text(s, "A star will fall!", self.font_tiny, (90, 30, 90), (240, 256), center=True)
        # round table with crystal ball, cards and book
        pygame.draw.ellipse(s, (70, 30, 80), (360, 362, 240, 40))
        pygame.draw.polygon(s, (70, 30, 80), [(362, 382), (598, 382), (620, 430), (340, 430)])
        for k in range(9):
            x = 350 + k * 30
            pygame.draw.line(s, (90, 46, 100), (x, 386), (x - 4 + k, 430), 2)
        pygame.draw.line(s, GOLD, (340, 430), (620, 430), 3)
        glow(s, (481, 343), 70, (120, 220, 255), 70 + 30 * math.sin(self.t * 2))
        pygame.draw.circle(s, (130, 200, 230), (481, 343), 24)
        pygame.draw.circle(s, (220, 245, 255), (472, 334), 6)
        pygame.draw.rect(s, GOLD, (466, 364, 30, 8))
        for k in range(4):
            pygame.draw.rect(s, (220, 210, 180), (524 + k * 16, 364 + k % 2 * 3, 14, 20), border_radius=2)
            pygame.draw.rect(s, (90, 40, 90), (524 + k * 16, 364 + k % 2 * 3, 14, 20), 1, border_radius=2)
        pygame.draw.rect(s, (60, 30, 30), (396, 362, 48, 16))
        pygame.draw.rect(s, PAPER, (400, 360, 40, 14))
        pygame.draw.line(s, INK, (420, 360), (420, 374), 1)
        # incense smoke
        pygame.draw.rect(s, GOLD, (700, 400, 10, 30))
        for k in range(6):
            pygame.draw.circle(s, (120, 110, 130), (int(705 + 6 * math.sin(self.t * 2 + k)), 392 - k * 12), 3)

    def draw_caravans(self, s):
        # distant ferris wheel
        cx, cy = 640, 210
        pygame.draw.circle(s, (60, 50, 80), (cx, cy), 120, 3)
        for k in range(10):
            a = k * math.pi / 5 + self.t * 0.15
            ex, ey = cx + 120 * math.cos(a), cy + 120 * math.sin(a)
            pygame.draw.line(s, (50, 42, 66), (cx, cy), (ex, ey), 1)
            pygame.draw.circle(s, BULB_COLORS[k % 5], (int(ex), int(ey)), 4)
        pygame.draw.line(s, (50, 42, 66), (cx, cy), (cx - 60, 430), 4)
        pygame.draw.line(s, (50, 42, 66), (cx, cy), (cx + 60, 430), 4)
        draw_string_lights(s, (0, 80), (960, 90), 70, self.t, 18)
        # Pip's caravan
        self.draw_caravan(s, (170, 220, 230, 170), (120, 60, 70))
        pygame.draw.rect(s, (90, 40, 50), (330, 280, 50, 110))
        pygame.draw.circle(s, RED, (355, 310), 12)
        pygame.draw.rect(s, (60, 60, 66), (322, 392, 66, 8))
        pygame.draw.polygon(s, (120, 70, 50), [(336, 400), (372, 400), (368, 432), (340, 432)])
        for a in (-0.5, 0, 0.5):
            end = (354 + 20 * math.sin(a), 400 - 26 * math.cos(a))
            pygame.draw.line(s, (60, 100, 60), (354, 400), end, 2)
            pygame.draw.circle(s, (240, 200, 80), (int(end[0]), int(end[1])), 4)
        # Lia's caravan with a lit window
        self.draw_caravan(s, (540, 230, 230, 160), (60, 80, 110))
        pygame.draw.rect(s, (255, 205, 120), (580, 260, 70, 50))
        glow(s, (615, 285), 60, (255, 205, 120), 70)
        pygame.draw.line(s, (60, 80, 110), (615, 260), (615, 310), 3)
        pygame.draw.rect(s, (60, 60, 66), (680, 392, 60, 8))
        pygame.draw.rect(s, (60, 60, 66), (690, 412, 50, 8))
        pygame.draw.ellipse(s, (230, 230, 230), (694, 404, 38, 28))
        pygame.draw.line(s, (180, 180, 180), (700, 410), (726, 410), 2)
        for k in range(5):
            pygame.draw.circle(s, (240, 240, 240), (712 + k * 5, 436 + k % 2), 1)

    def draw_caravan(self, s, rect, color):
        x, y, w, h = rect
        pygame.draw.rect(s, color, (x, y + 20, w, h - 20), border_radius=10)
        pygame.draw.ellipse(s, shade(color, 15), (x - 6, y, w + 12, 50))
        for k in range(0, w, 18):
            pygame.draw.line(s, shade(color, -15), (x + k, y + 40), (x + k, y + h - 10), 1)
        pygame.draw.line(s, GOLD, (x, y + h - 30), (x + w, y + h - 30), 3)
        for wx in (x + 40, x + w - 40):
            pygame.draw.circle(s, (30, 26, 24), (wx, y + h + 8), 22)
            pygame.draw.circle(s, GOLD, (wx, y + h + 8), 22, 3)
            for k in range(6):
                a = k * math.pi / 3
                pygame.draw.line(s, GOLD, (wx, y + h + 8), (wx + 18 * math.cos(a), y + h + 8 + 18 * math.sin(a)), 2)

    # ---------------------------------------------------------- intro scenes

    def draw_scene(self, s, name, weather, shade_alpha=0):
        s.blit(self.scenes[name], (0, 0))
        self.draw_weather(s, weather)
        if shade_alpha:
            shade_screen(s, shade_alpha)

    def draw_weather(self, s, weather):
        for x, y, size, phase in self.particles:
            if weather == "rain":
                pygame.draw.line(s, (150, 160, 180), (x, y), (x - 4, y + 14), 1)
            elif weather == "snow":
                pygame.draw.circle(s, (235, 238, 245), (int(x + 12 * math.sin(phase)), int(y)), int(1 + size))
            else:
                color = BULB_COLORS[int(x) % len(BULB_COLORS)]
                w = int(4 * abs(math.cos(phase)) + 1)
                pygame.draw.rect(s, color, (int(x + 10 * math.sin(phase)), int(y), w, 4))

    def draw_case_scene(self, s, shade_alpha=0):
        self.draw_scene(s, self.theme["scene"], self.theme["weather"], shade_alpha)

    # ------------------------------------------------------------- case file

    def draw_case_file(self, s):
        story = self.case["story"]
        folder = pygame.Rect(36, 34, 888, 548)
        pygame.draw.rect(s, (196, 166, 112), folder, border_radius=8)
        pygame.draw.rect(s, (196, 166, 112), (folder.x, folder.y - 22, 210, 30), border_radius=8)
        draw_text(s, "CASE FILE No. %d" % (self.case_index + 1), self.font_small_bold, INK,
                  (folder.x + 105, folder.y - 8), center=True)
        page = pygame.Rect(54, 50, 852, 500)
        pygame.draw.rect(s, (150, 124, 84), page.move(4, 4), border_radius=4)
        pygame.draw.rect(s, PAPER, page, border_radius=4)
        for y in range(page.y + 40, page.bottom - 10, 22):
            pygame.draw.line(s, (222, 210, 178), (page.x + 10, y), (page.right - 10, y), 1)
        # coffee ring and paper clip for a used look
        pygame.draw.circle(s, (205, 180, 140), (page.right - 70, page.bottom - 60), 30, 4)
        pygame.draw.rect(s, (150, 150, 158), (page.x + 30, page.y - 12, 14, 46), 3, border_radius=7)
        stamp = self.font_big.render("CONFIDENTIAL", True, (190, 40, 50))
        stamp = pygame.transform.rotate(stamp, 12)
        stamp.set_alpha(110)
        s.blit(stamp, (page.x + 120, page.bottom - 110))
        draw_text(s, self.case["title"], self.font_big, INK, (page.x + 60, page.y + 10))

        # left column: the stolen item and the client
        x = page.x + 24
        y = page.y + 56
        draw_text(s, story["item_label"], self.font_small_bold, (160, 30, 40), (x, y))
        picture = pygame.Rect(x, y + 24, 150, 130)
        pygame.draw.rect(s, (30, 30, 36), picture)
        self.draw_case_item(s, picture.inflate(-10, -10), story["art"])
        pygame.draw.rect(s, WHITE, picture, 4)
        pygame.draw.line(s, (170, 170, 170), (picture.x + 8, picture.y - 4), (picture.x + 40, picture.y + 10), 6)
        draw_text(s, story["item"], self.font_bold, INK, (x + 162, y + 22))
        ty = draw_text_block(s, story["about"], self.font_small, INK, x + 162, y + 46, 238, gap=1)
        ty = max(ty, picture.bottom) + 16
        draw_text(s, "THE CLIENT", self.font_small_bold, (160, 30, 40), (x, ty))
        draw_text_block(s, story["client"], self.font_small, INK, x, ty + 20, 400, gap=1)

        # right column: timeline and suspects
        rx = page.x + 446
        pygame.draw.line(s, (200, 180, 140), (rx - 18, page.y + 56), (rx - 18, page.bottom - 16), 2)
        y = page.y + 56
        draw_text(s, "WHAT WE KNOW", self.font_small_bold, (160, 30, 40), (rx, y))
        y += 22
        for time, event in story["timeline"]:
            pygame.draw.circle(s, (160, 30, 40), (rx + 4, y + 8), 4)
            draw_text(s, time, self.font_small_bold, INK, (rx + 14, y))
            y = draw_text_block(s, event, self.font_small, INK, rx + 62, y, 320, gap=0) + 3
        y += 10
        draw_text(s, "THE SUSPECTS", self.font_small_bold, (160, 30, 40), (rx, y))
        y += 22
        for sid, sus in self.suspects.items():
            pygame.draw.circle(s, sus["accent"], (rx + 5, y + 9), 5)
            name = "%s (%s)" % (sus["name"], sus["role"])
            draw_text(s, name, self.font_small_bold, INK, (rx + 16, y))
            y = draw_text_block(s, story["bios"][sid], self.font_small, (80, 64, 48), rx + 16, y + 16, 366, gap=0) + 4

        hint = "Press SPACE to start the investigation" if self.file_first else "Press SPACE or F to close"
        if int(self.t * 1.5) % 2 == 0:
            draw_text(s, hint, self.font_bold, WHITE, (WIDTH // 2, 588), center=True)

    def draw_case_item(self, s, rect, art):
        r = pygame.Rect(rect)
        cx, cy = r.center
        if art == "painting":
            vertical_gradient(s, r, (20, 26, 52), (60, 70, 110))
            pygame.draw.circle(s, (240, 235, 200), (r.right - 34, r.y + 28), 14)
            glow(s, (r.right - 34, r.y + 28), 34, (240, 235, 200), 60)
            pygame.draw.polygon(s, (24, 30, 40), [(r.x, r.bottom - 30), (r.x + 50, r.bottom - 52), (r.x + 90, r.bottom - 34),
                                                  (r.right, r.bottom - 48), r.bottomright, r.bottomleft])
            for k in range(5):
                pygame.draw.line(s, (240, 235, 200), (r.right - 50 + k * 4, r.bottom - 26 + k * 4),
                                 (r.right - 30 - k * 3, r.bottom - 26 + k * 4), 1)
            pygame.draw.polygon(s, (60, 40, 30), [(cx - 20, r.bottom - 14), (cx + 16, r.bottom - 14), (cx + 10, r.bottom - 6), (cx - 14, r.bottom - 6)])
            pygame.draw.line(s, (60, 40, 30), (cx - 2, r.bottom - 14), (cx - 2, r.bottom - 40), 2)
            pygame.draw.rect(s, GOLD, r, 6)
        elif art == "necklace":
            pygame.draw.rect(s, (60, 20, 34), r)
            points = []
            for k in range(21):
                a = math.pi * 0.1 + math.pi * 0.8 * k / 20
                points.append((cx - math.cos(a) * 52, r.y + 14 + math.sin(a) * 60))
            for px, py in points:
                pygame.draw.circle(s, (210, 230, 255), (int(px), int(py)), 3)
            star_center = (cx, r.y + 88)
            glow(s, star_center, 40, (170, 215, 255), 120)
            pts = []
            for k in range(10):
                rad = 18 if k % 2 == 0 else 8
                a = -math.pi / 2 + k * math.pi / 5
                pts.append((star_center[0] + rad * math.cos(a), star_center[1] + rad * math.sin(a)))
            pygame.draw.polygon(s, (215, 240, 255), pts)
            pygame.draw.polygon(s, (120, 170, 220), pts, 1)
            pygame.draw.circle(s, WHITE, (star_center[0] - 4, star_center[1] - 6), 2)
        elif art == "formula":
            pygame.draw.rect(s, (30, 60, 110), r)
            for k in range(0, r.w, 12):
                pygame.draw.line(s, (50, 84, 140), (r.x + k, r.y), (r.x + k, r.bottom), 1)
            for k in range(0, r.h, 12):
                pygame.draw.line(s, (50, 84, 140), (r.x, r.y + k), (r.right, r.y + k), 1)
            pygame.draw.rect(s, (220, 230, 250), (cx - 22, cy - 30, 44, 64), 2)
            pygame.draw.rect(s, (220, 230, 250), (cx - 8, cy - 38, 16, 8), 2)
            for k in range(3):
                pygame.draw.line(s, (220, 230, 250), (cx - 14, cy + 20 - k * 16), (cx + 14, cy + 20 - k * 16), 2)
            draw_text(s, "+", self.font_bold, (220, 230, 250), (cx, cy - 18), center=True)
            draw_text(s, "x10", self.font_small_bold, YELLOW, (r.x + 22, r.y + 14), center=True)
            draw_text(s, "Li-C6", self.font_tiny, (220, 230, 250), (r.right - 26, r.bottom - 12), center=True)
        elif art == "egg":
            pygame.draw.rect(s, (40, 22, 30), r)
            glow(s, (cx, cy - 6), 60, GOLD, 90)
            egg = pygame.Rect(cx - 30, cy - 46, 60, 78)
            pygame.draw.ellipse(s, (226, 178, 62), egg)
            pygame.draw.ellipse(s, (250, 215, 120), egg.inflate(-34, -50).move(-8, -14))
            for k in range(-2, 3):
                pygame.draw.arc(s, (150, 100, 30), egg.inflate(-abs(k) * 18, 0), -1.2, 1.2, 1)
            for k, color in enumerate(((210, 40, 60), (40, 170, 90), (210, 40, 60), (40, 170, 90), (210, 40, 60))):
                pygame.draw.circle(s, color, (cx - 20 + k * 10, cy - 6 + (k % 2) * 6), 4)
            pygame.draw.circle(s, (210, 40, 60), (cx, egg.y + 8), 5)
            pygame.draw.polygon(s, (150, 110, 40), [(cx - 22, egg.bottom - 2), (cx + 22, egg.bottom - 2), (cx + 30, r.bottom - 6), (cx - 30, r.bottom - 6)])
        elif art == "trapeze":
            vertical_gradient(s, r, (60, 14, 30), (20, 8, 20))
            alpha_polygon(s, (255, 220, 120), 50, [(cx - 6, r.y), (cx + 6, r.y), (cx + 50, r.bottom), (cx - 50, r.bottom)])
            pygame.draw.line(s, (220, 210, 190), (cx - 34, r.y), (cx - 34, r.y + 60), 2)
            pygame.draw.line(s, (220, 210, 190), (cx + 34, r.y), (cx + 34, r.y + 26), 2)
            pygame.draw.line(s, (220, 210, 190), (cx + 34, r.y + 26), (cx + 30, r.y + 34), 1)
            pygame.draw.line(s, GOLD, (cx - 34, r.y + 60), (cx + 10, r.y + 84), 4)
            # Stella falling into the net
            pygame.draw.circle(s, (230, 230, 230), (cx + 22, r.y + 70), 6)
            pygame.draw.line(s, (230, 230, 230), (cx + 22, r.y + 76), (cx + 32, r.y + 94), 4)
            pygame.draw.line(s, (230, 230, 230), (cx + 26, r.y + 82), (cx + 40, r.y + 76), 2)
            for k in range(9):
                x = r.x + 10 + k * 14
                pygame.draw.line(s, (200, 190, 170), (x, r.bottom - 22), (x + 10, r.bottom - 8), 1)
                pygame.draw.line(s, (200, 190, 170), (x + 10, r.bottom - 22), (x, r.bottom - 8), 1)
            pygame.draw.line(s, (200, 190, 170), (r.x + 6, r.bottom - 22), (r.right - 6, r.bottom - 22), 2)

    # --------------------------------------------------------------- overlays

    def draw_message(self, s):
        box = pygame.Rect(80, 400, 800, 185)
        panel(s, box)
        draw_text(s, self.message["title"], self.font_big, GOLD, (box.x + 24, box.y + 16))
        y = draw_text_block(s, self.message["text"], self.font, WHITE,
                            box.x + 24, box.y + 58, box.w - 48)
        if self.message["note"]:
            draw_text(s, self.message["note"], self.font_bold, ORANGE, (box.x + 24, y + 6))
        draw_text(s, "SPACE to continue", self.font_small, GREY, (box.right - 140, box.bottom - 24))

    def draw_notebook(self, s):
        shade_screen(s, 150)
        page = pygame.Rect(30, 56, 900, 536)
        pygame.draw.rect(s, PAPER, page, border_radius=6)
        pygame.draw.rect(s, (138, 90, 43), page, 6, border_radius=6)
        pygame.draw.line(s, (200, 120, 120), (page.x + 18, page.y + 10), (page.x + 18, page.bottom - 10), 1)
        draw_text(s, "Detective's Notebook", self.font_big, INK, (page.x + 30, page.y + 14))
        draw_text(s, "%d of %d clues" % (len(self.found), len(self.clues)), self.font,
                  (110, 80, 50), (page.right - 150, page.y + 22))
        pygame.draw.line(s, (180, 150, 110), (page.x + 20, page.y + 56), (page.right - 20, page.y + 56), 2)
        if not self.found:
            draw_text(s, "No clues yet. Look around!", self.font, INK, (page.x + 30, page.y + 76))
        per_col = len(self.found) if len(self.found) <= 4 else (len(self.found) + 1) // 2
        col_w = 820 if len(self.found) <= 4 else 400
        y_start = page.y + 68
        y = y_start
        for i, cid in enumerate(self.found):
            if i == per_col:
                y = y_start
            x = page.x + 30 + (430 if i >= per_col else 0)
            title, text = self.clues[cid]
            draw_text(s, title, self.font_bold, (140, 30, 30), (x, y))
            y = draw_text_block(s, text, self.font_small, INK, x, y + 22, col_w, gap=2) + 10
        draw_text(s, "click or press N to close", self.font_small, (110, 80, 50),
                  (page.centerx, page.bottom - 16), center=True)

    def draw_howto(self, s):
        box = pygame.Rect(70, 30, 820, 540)
        panel(s, box, 240)
        draw_text(s, "How to Play", self.font_title, GOLD, (WIDTH // 2, 72), center=True)
        y = 112
        for i, (title, text) in enumerate(HOW_TO_PLAY):
            pygame.draw.circle(s, GOLD, (118, y + 12), 15)
            draw_text(s, str(i + 1), self.font_bold, BLACK, (118, y + 12), center=True)
            draw_text(s, title, self.font_bold, GOLD, (148, y))
            y = draw_text_block(s, text, self.font_small, WHITE, 148, y + 24, 700) + 12
        keys = "Arrows: walk   SPACE: examine / talk   1-6: questions   F: File   N: Notebook   A: Accuse   Esc: Menu"
        draw_text(s, keys, self.font_small_bold, LIGHT_GREY, (WIDTH // 2, y + 10), center=True)
        if int(self.t * 1.5) % 2 == 0:
            draw_text(s, "Press any key to continue", self.font_bold, WHITE, (WIDTH // 2, box.bottom - 26), center=True)

    # ------------------------------------------------------------------ talk

    def talk_options(self):
        topics = self.suspects[self.talk_id]["topics"]
        options = [(i, t["q"]) for i, t in enumerate(topics)
                   if t.get("req") is None or t["req"] in self.found]
        options.append((None, "Goodbye."))
        rects = [pygame.Rect(545, 345 + n * 38, 380, 32) for n in range(len(options))]
        return list(zip(options, rects))

    def click_talk(self, pos):
        for (idx, _), rect in self.talk_options():
            if rect.collidepoint(pos):
                self.choose_topic(idx)

    def choose_topic(self, idx):
        if idx is None:
            self.state = "explore"
            return
        self.talk_text = self.suspects[self.talk_id]["topics"][idx]["a"]
        if (self.talk_id, idx) not in self.asked:
            self.asked.add((self.talk_id, idx))
            self.add_points(POINTS_QUESTION, 480, 320)

    def draw_talk(self, s, mouse):
        sus = self.suspects[self.talk_id]
        box = pygame.Rect(20, 330, 920, 258)
        panel(s, box, 240)
        portrait = pygame.Rect(36, 346, 140, 226)
        vertical_gradient(s, portrait, (56, 58, 66), (24, 24, 28))
        s.set_clip(portrait)
        glow(s, (portrait.centerx, portrait.y + 60), 70, sus["accent"], 50)
        draw_person(s, portrait.centerx, portrait.bottom + 30, sus["style"], sus["accent"])
        s.set_clip(None)
        pygame.draw.rect(s, sus["accent"], portrait, 2, border_radius=6)
        draw_text(s, sus["name"], self.font_big, GOLD, (196, 344))
        draw_text(s, sus["role"], self.font_small, LIGHT_GREY, (196, 378))
        draw_text_block(s, '"' + self.talk_text + '"', self.font, WHITE, 196, 404, 330, gap=1)
        for (idx, question), rect in self.talk_options():
            hover = rect.collidepoint(mouse)
            asked = (self.talk_id, idx) in self.asked
            color = WHITE if hover else (GREY if asked else GOLD)
            if hover:
                pygame.draw.rect(s, (45, 38, 22), rect, border_radius=5)
            pygame.draw.rect(s, color, rect, 1, border_radius=5)
            number = self.talk_options().index(((idx, question), rect)) + 1
            draw_text(s, "%d.  %s" % (number, question), self.font_small if idx is not None else self.font_bold,
                      color, (rect.x + 10, rect.y + 7))

    # ---------------------------------------------------------------- accuse

    def start_accuse(self):
        if len(self.found) < self.case["min_clues"]:
            self.show_message("Not so fast!",
                              "You need at least %d clues before you can accuse anyone. "
                              "You have %d. Keep investigating."
                              % (self.case["min_clues"], len(self.found)))
            return
        self.accuse_step = "suspect"
        self.accuse_suspect = None
        self.selected = []
        self.state = "accuse"

    def suspect_cards(self):
        ids = list(self.suspects)
        w = min(200, (WIDTH - 60) // len(ids) - 16)
        total = len(ids) * w + (len(ids) - 1) * 16
        x0 = (WIDTH - total) // 2
        return [(sid, pygame.Rect(x0 + i * (w + 16), 140, w, 280)) for i, sid in enumerate(ids)]

    def evidence_buttons(self):
        buttons = []
        n = len(self.found)
        per_col = n if n <= 4 else (n + 1) // 2
        for i, cid in enumerate(self.found):
            if n > 4:
                rect = pygame.Rect(120 + (i // per_col) * 370, 140 + (i % per_col) * 56, 350, 46)
            else:
                rect = pygame.Rect(230, 150 + i * 58, 500, 46)
            buttons.append((cid, rect))
        return buttons

    def back_button(self):
        if self.accuse_step == "suspect":
            return pygame.Rect(380, 520, 200, 44)
        return pygame.Rect(250, 520, 200, 44)

    def confirm_button(self):
        return pygame.Rect(510, 520, 200, 44)

    def click_accuse(self, pos):
        if self.back_button().collidepoint(pos):
            if self.accuse_step == "evidence":
                self.accuse_step = "suspect"
                self.selected = []
            else:
                self.state = "explore"
            return
        if self.accuse_step == "suspect":
            for sid, rect in self.suspect_cards():
                if rect.collidepoint(pos):
                    self.accuse_suspect = sid
                    self.accuse_step = "evidence"
            return
        for cid, rect in self.evidence_buttons():
            if rect.collidepoint(pos):
                if cid in self.selected:
                    self.selected.remove(cid)
                else:
                    self.selected.append(cid)
                    if len(self.selected) > self.case["evidence"]:
                        self.selected.pop(0)
        if (self.confirm_button().collidepoint(pos)
                and len(self.selected) == self.case["evidence"]):
            self.judge(self.accuse_suspect, self.selected)

    def judge(self, sid, chosen):
        strong = self.case["strong"]
        if sid == self.case["culprit"] and all(c in strong for c in chosen):
            self.result = "win"
            self.bonus = POINTS_SOLVED + 100 * self.attempts_left()
            self.score += self.bonus
            self.record_highscore()
            stars = max(1, 3 - self.mistakes)
            if len(self.stars) > self.case_index:
                # case was replayed from the menu: keep the better result
                self.stars[self.case_index] = max(self.stars[self.case_index], stars)
            else:
                self.stars.append(stars)
            self.state = "ending"
            return
        self.mistakes += 1
        self.add_points(POINTS_WRONG, 480, 300)
        if sid != self.case["culprit"]:
            title = "Wrong suspect!"
            text = self.suspects[sid]["innocent"]
        else:
            title = "Not enough proof!"
            weak = [c for c in chosen if c not in strong][0]
            text = self.case["weak_text"].get(
                weak, "'%s' does not prove anything against %s."
                % (self.clues[weak][0], self.suspects[sid]["name"]))
        if self.attempts_left() <= 0:
            self.result = "lose"
            self.record_highscore()
            self.show_message(title, text, "That was your last attempt...", after="ending")
        else:
            self.show_message(title, text, "Attempts left: %d" % self.attempts_left())

    def draw_accuse(self, s, mouse):
        shade_screen(s, 210)
        if self.accuse_step == "suspect":
            draw_text(s, self.case["question"], self.font_big, GOLD, (WIDTH // 2, 95), center=True)
            for sid, rect in self.suspect_cards():
                sus = self.suspects[sid]
                hover = rect.collidepoint(mouse)
                vertical_gradient(s, rect, (52, 54, 62) if hover else (34, 34, 40), (14, 14, 18))
                pygame.draw.rect(s, sus["accent"] if hover else GREY, rect, 2, border_radius=8)
                s.set_clip(rect)
                if hover:
                    glow(s, (rect.centerx, rect.y + 70), 70, sus["accent"], 60)
                draw_person(s, rect.centerx, rect.y + 215, sus["style"], sus["accent"])
                s.set_clip(None)
                name_font = self.font_bold if self.font_bold.size(sus["name"])[0] < rect.w - 8 else self.font_small_bold
                draw_text(s, sus["name"], name_font, WHITE, (rect.centerx, rect.y + 238), center=True)
                draw_text(s, sus["role"], self.font_small, LIGHT_GREY, (rect.centerx, rect.y + 260), center=True)
            draw_text(s, "Attempts left: %d" % self.attempts_left(), self.font,
                      LIGHT_GREY, (WIDTH // 2, 470), center=True)
            self.draw_button(s, self.back_button(), "Cancel", mouse, GREY)
            return
        need = self.case["evidence"]
        name = self.suspects[self.accuse_suspect]["name"]
        title = ("Which clue proves that %s did it?" % name if need == 1 else
                 "Choose %d clues that prove %s did it" % (need, name))
        draw_text(s, title, self.font_big, GOLD, (WIDTH // 2, 95), center=True)
        for cid, rect in self.evidence_buttons():
            chosen = cid in self.selected
            hover = rect.collidepoint(mouse)
            fill = (70, 25, 30) if chosen else ((45, 38, 22) if hover else DARK)
            pygame.draw.rect(s, fill, rect, border_radius=6)
            pygame.draw.rect(s, RED if chosen else (WHITE if hover else GOLD), rect, 2, border_radius=6)
            label = ("> " if chosen else "") + self.clues[cid][0]
            draw_text(s, label, self.font_bold, WHITE if chosen or hover else GOLD,
                      rect.center, center=True)
        draw_text(s, "Selected: %d / %d     Attempts left: %d"
                  % (len(self.selected), need, self.attempts_left()),
                  self.font, LIGHT_GREY, (WIDTH // 2, 470), center=True)
        self.draw_button(s, self.back_button(), "Back", mouse, GREY)
        self.draw_button(s, self.confirm_button(), "Accuse!", mouse, RED,
                         enabled=len(self.selected) == need)

    # ----------------------------------------------------------------- screens

    def draw_title(self, s):
        self.draw_scene(s, "city", "rain")
        panel(s, (130, 30, 700, 266), 215)
        draw_text(s, "SHADOW DETECTIVE", self.font_title, GOLD, (WIDTH // 2, 80), center=True)
        draw_text(s, "Five cases. One detective. Nobody tells the whole truth.",
                  self.font, LIGHT_GREY, (WIDTH // 2, 128), center=True)
        for i, case in enumerate(CASES):
            rect = draw_text(s, "Case %d: %s" % (i + 1, case["title"]), self.font_small,
                             WHITE, (WIDTH // 2, 162 + i * 22), center=True)
            if i < len(self.stars):
                for k in range(3):
                    draw_star(s, (rect.right + 14 + k * 16, rect.centery), k < self.stars[i], 6)
        draw_text(s, "High score: %d" % self.highscore, self.font_small_bold, YELLOW,
                  (WIDTH // 2, 278), center=True)
        if self.resume_state:
            mouse = pygame.mouse.get_pos()
            self.draw_button(s, self.continue_button(), "Continue - Case %d  [Enter]" % (self.case_index + 1), mouse)
            self.draw_button(s, self.new_game_button(), "New Game  [N]", mouse, GREY)
        elif int(self.t * 1.5) % 2 == 0:
            draw_text(s, "PRESS ANY KEY TO START", self.font_big, WHITE, (WIDTH // 2, 570), center=True)

    def draw_case_intro(self, s):
        self.draw_case_scene(s, 40)
        box = pygame.Rect(90, 24, 780, 440)
        panel(s, box, 225)
        draw_text(s, "CASE %d" % (self.case_index + 1), self.font_bold, LIGHT_GREY,
                  (WIDTH // 2, 52), center=True)
        draw_text(s, self.case["title"], self.font_title, GOLD, (WIDTH // 2, 94), center=True)
        y = draw_text_block(s, self.case["intro"], self.font, WHITE, 125, 135, 710)
        y += 12
        draw_text(s, "Rules for this case:", self.font_bold, GOLD, (125, y))
        if self.case["glow"] >= 1:
            glow_rule = "Clues glow brightly."
        elif self.case["glow"] > 0:
            glow_rule = "Clues only glow faintly."
        else:
            glow_rule = "Clues do NOT glow - look at everything!"
        evidence = self.case["evidence"]
        attempts = self.case["attempts"]
        rules = [
            "Find at least %d clues before you may accuse someone." % self.case["min_clues"],
            "Pick %d clue%s as evidence when you accuse." % (evidence, "" if evidence == 1 else "s"),
            "You have only 1 attempt - no second chance!" if attempts == 1
            else "You have %d attempts." % attempts,
            glow_rule,
            "Watch out for the %s! Every bump costs 50 points." % self.theme["enemy_name"],
        ]
        for rule in rules:
            y += 24
            pygame.draw.circle(s, GOLD, (135, y + 10), 3)
            draw_text(s, rule, self.font_small, WHITE, (148, y + 2))
        if int(self.t * 1.5) % 2 == 0:
            draw_text(s, "Press any key to open the case file", self.font_bold, WHITE,
                      (WIDTH // 2, 575), center=True)

    def end_button_rect(self):
        return pygame.Rect(250, 520, 220, 44)

    def end_button_pressed(self):
        if self.state == "finale":
            self.new_game()
        elif self.result == "win":
            if self.case_index + 1 < len(CASES):
                self.case_index += 1
                self.start_case()
            else:
                self.state = "finale"
        else:
            self.start_case(restart=True)

    def exit_button_rect(self):
        return pygame.Rect(490, 520, 220, 44)

    def draw_ending(self, s, mouse):
        self.draw_case_scene(s, 120)
        box = pygame.Rect(100, 24, 760, 482)
        panel(s, box, 230)
        if self.result == "win":
            draw_text(s, "CASE CLOSED", self.font_title, GOLD, (WIDTH // 2, 74), center=True)
            for i in range(3):
                draw_star(s, (WIDTH // 2 - 60 + i * 60, 134), i < self.stars[self.case_index])
            draw_text(s, self.case["confession"], self.font_big, WHITE, (WIDTH // 2, 184), center=True)
            y = draw_text_block(s, self.case["solution"], self.font, LIGHT_GREY,
                                box.x + 36, 214, box.w - 72, gap=2)
            draw_text(s, "What happened next:", self.font_small_bold, GOLD, (box.x + 36, y + 8))
            y = draw_text_block(s, self.case["story"]["epilogue"], self.font_small, WHITE,
                                box.x + 36, y + 26, box.w - 72, gap=2)
            draw_text(s, "Clues: %d of %d     Case bonus: +%d     Score: %d"
                      % (len(self.found), len(self.clues), self.bonus, self.score),
                      self.font_small_bold, YELLOW, (WIDTH // 2, y + 12), center=True)
            last = self.case_index + 1 == len(CASES)
            label = "Final results" if last else "Next case"
        else:
            draw_text(s, "THE CULPRIT ESCAPED", self.font_title, RED, (WIDTH // 2, 85), center=True)
            draw_text(s, "You ran out of attempts.", self.font_big, WHITE, (WIDTH // 2, 160), center=True)
            draw_text(s, "Score: %d" % self.score, self.font_big, YELLOW, (WIDTH // 2, 215), center=True)
            draw_text(s, "High score: %d" % self.highscore, self.font_small_bold, LIGHT_GREY,
                      (WIDTH // 2, 250), center=True)
            tip = ("Tip: Read your notebook carefully and ask every suspect about every clue. "
                   "Who had a reason? Who had the chance? And who is lying?")
            draw_text_block(s, tip, self.font, LIGHT_GREY, box.x + 60, 290, box.w - 120)
            draw_text(s, "Trying again resets the points of this case.", self.font_small, GREY,
                      (WIDTH // 2, 470), center=True)
            label = "Try again"
        self.draw_button(s, self.end_button_rect(), label + " [Enter]", mouse)
        self.draw_button(s, self.exit_button_rect(), "Exit to title [X]", mouse, RED)

    def draw_finale(self, s, mouse):
        self.draw_scene(s, "city", "rain", 120)
        box = pygame.Rect(130, 24, 700, 482)
        panel(s, box, 230)
        draw_text(s, "ALL CASES SOLVED", self.font_title, GOLD, (WIDTH // 2, 72), center=True)
        total = sum(self.stars)
        best = 3 * len(CASES)
        for i, (case, stars) in enumerate(zip(CASES, self.stars)):
            y = 136 + i * 38
            draw_text(s, "Case %d: %s" % (i + 1, case["title"]), self.font, WHITE, (190, y - 10))
            for k in range(3):
                draw_star(s, (660 + k * 36, y), k < stars, 14)
        if total == best:
            rank = "Master Detective"
        elif total >= best * 0.6:
            rank = "Senior Inspector"
        else:
            rank = "Rookie Detective"
        draw_text(s, "FINAL SCORE: %d" % self.score, self.font_big, YELLOW, (WIDTH // 2, 345), center=True)
        draw_text(s, "%d / %d stars  -  Rank: %s" % (total, best, rank), self.font_bold, WHITE,
                  (WIDTH // 2, 390), center=True)
        if self.new_highscore:
            if int(self.t * 3) % 2 == 0:
                draw_text(s, "NEW HIGH SCORE!", self.font_big, ORANGE, (WIDTH // 2, 440), center=True)
        else:
            draw_text(s, "High score: %d" % self.highscore, self.font_bold, LIGHT_GREY,
                      (WIDTH // 2, 440), center=True)
        self.draw_button(s, self.end_button_rect(), "Play again [Enter]", mouse)
        self.draw_button(s, self.exit_button_rect(), "Exit to title [X]", mouse, RED)

    def draw(self):
        s = self.screen
        mouse = pygame.mouse.get_pos()
        if self.state == "menu":
            # draw the paused screen underneath, then the menu on top
            self.state = self.menu_return
            self.draw()
            self.state = "menu"
            self.draw_menu(s, mouse)
            return
        if self.state in ("case_intro", "case_file", "ending", "finale"):
            self.draw_screen(s, mouse)
            self.draw_button(s, self.corner_menu_button(), "Menu [Esc]", mouse, GREY)
            return
        self.draw_screen(s, mouse)

    def draw_screen(self, s, mouse):
        if self.state == "title":
            self.draw_title(s)
        elif self.state == "case_intro":
            self.draw_case_intro(s)
        elif self.state == "case_file":
            self.draw_case_scene(s, 150)
            self.draw_case_file(s)
        elif self.state == "ending":
            self.draw_ending(s, mouse)
        elif self.state == "finale":
            self.draw_finale(s, mouse)
        elif self.state == "howto" and self.howto_return != "explore":
            self.draw_case_scene(s, 100)
            self.draw_howto(s)
        else:
            self.draw_room(s)
            self.draw_top_bar(s, mouse)
            self.draw_hud(s)
            if self.state == "explore":
                self.draw_prompt(s)
            elif self.state == "message":
                self.draw_message(s)
            elif self.state == "notebook":
                self.draw_notebook(s)
            elif self.state == "talk":
                self.draw_talk(s, mouse)
            elif self.state == "accuse":
                self.draw_accuse(s, mouse)
            elif self.state == "howto":
                shade_screen(s, 120)
                self.draw_howto(s)



if __name__ == "__main__":
    Game().run()
