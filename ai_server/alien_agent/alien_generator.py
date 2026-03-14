import random
import sys
import os

# Ensure the directory containing this file is always on sys.path
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

class Alien:

    def __init__(self):
        # ── Random Identity Generation ────────────────────────────────────────
        self.__name = self.get_random_name()
        self.__mood = self.get_random_mood()
        self.__mbti = self.get_random_mbti()
        self.__situation = self.get_random_market_booth()
        self.__greeting = self.get_random_greeting()
        
        # ── Fixed List Logic ──────────────────────────────────────────────────
        self.__likes = self.get_random_likes()
        self.__dislikes = self.get_random_dislikes(self.__likes)

        # ── AI & Game State ───────────────────────────────────────────────────
        self.adk_session = None  # This stores the Runner from agent.py
        self.__turn = 0
        self.__summaries = []

    # ── AI Session Methods ────────────────────────────────────────────────────
    
    def set_session(self, runner):
        """Called by agent.py to link the Gemini Runner to this alien instance."""
        self.adk_session = runner

    def get_prompt(self):
        """Generates the system instruction for Gemini based on this alien's traits."""
        return (
            f"You name is {self.__name}. You are an alien. Your mood is {self.__mood} and "
            f"you're an {self.__mbti}. You work as a {self.__situation[0]}, and you are situated in a "
            f"booth at a market where you are selling {self.__situation[1]}. You enjoy {self.__likes[0]}, "
            f"{self.__likes[1]}, and {self.__likes[2]}. You hate {self.__dislikes[0]}, {self.__dislikes[1]}, and "
            f"{self.__dislikes[2]}. You have a maximum dialog of 5 responses before you want to end "
            f"the conversation. Your greeting is \"{self.__greeting}\". I am looking to invite you "
            f"to the grand opening for my restaurant, but you don't know that yet. All you "
            f"know is that I approached your booth."
        )

    # ── Game Logic Helpers ────────────────────────────────────────────────────

    def get_turn(self) -> int:
        return self.__turn

    def increment_turn(self):
        self.__turn += 1

    def add_summary(self, summary_text: str):
        self.__summaries.append(summary_text)

    def get_greeting(self) -> str:
        return self.__greeting

    def get_dict(self):
        """Returns a dictionary for the Godot frontend to read."""
        return {
            "name":      self.__name,
            "mood":      self.__mood,
            "mbti":      self.__mbti,
            "situation": self.__situation,
            "greeting":  self.__greeting,
            "likes":     self.__likes,
            "dislikes":  self.__dislikes,
            "turn":      self.__turn
        }
        
    # ── Randomization Logic ───────────────────────────────────────────────────
        
    def get_random_name(self):
        return random.choice(self.alien_names)

    def get_random_mood(self):
        return random.choice(self.moods)
            
    def get_random_mbti(self):
        return random.choice(self.mbti_types)

    def get_random_market_booth(self):    
        return random.choice(self.market_booths)

    def get_random_greeting(self):
        return random.choice(self.greetings)

    def get_random_likes(self):
        # random.sample is safer—it picks 3 unique items automatically
        return random.sample(self.master_likes_list, 3)
    
    def get_random_dislikes(self, current_likes):
        # Ensure we don't dislike something we already like
        available = [item for item in self.master_likes_list if item not in current_likes]
        return random.sample(available, 3)

    # ── Data Arrays ───────────────────────────────────────────────────────────

    alien_names = [
        "Krag-Vark", "Lumina", "X'ylar", "Glip-Glop", "Xenophon", "Sshirra",
        "Grozznok", "Syllis", "Q-Tox", "Zorp", "Valerax", "Xis", "Thrax", "Vex"
    ]

    market_booths = [
        ["Farmer", "Bananas"], ["Beekeeper", "Wildflower Honey"],
        ["Baker", "Sourdough Bread"], ["Blacksmith", "Hand-forged Skillets"],
        ["Florist", "Sunflowers"], ["Potter", "Ceramic Mugs"]
    ]

    mbti_types = [
        "entp", "intp", "esfj", "isfj", "estp", "istp", "enfj", "infj",
        "esfp", "isfp", "entj", "intj", "enfp", "infp", "estj", "istj"
    ]

    moods = [
        "Overexcited", "Hyper", "Frantic", "Anxious", "Chill", "Sleepy", 
        "Impatient", "Grumpy", "Bubbly", "Cheerful", "Shy", "Timid", 
        "Serious", "Brainy", "Formal", "Strict", "Mischievous"
    ]

    greetings = [
        "Hi, welcome to my booth!",
        "Good day, what's your name?",
        "Step closer, traveler, see what I've found.",
        "Are you buying, or just blocking the light?",
        "Greetings! Have you ever seen anything like this?",
        "Salutations, friend. What brings you to my stall?",
        "Blessings upon your hive. What can I do for you?"
    ]

    master_likes_list = [
        "culinary arts", "the game zorx", "rhythmic gymnastics", "street food",
        "architectural ruins", "maritime navigation", "experimental jazz",
        "speculative fiction", "terrestrial botany", "competitive sports",
        "abstract painting", "beekeeping", "meteorological phenomena",
        "haute couture", "amusement parks", "folk mythology",
        "mechanical watches", "oceanography", "cinematography"
    ]