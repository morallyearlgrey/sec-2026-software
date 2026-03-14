import random

class Alien:
    
    def __init__(self):
        self.adk_session = ""
        self.__name = self.get_random_name()
        self.__mood = self.get_random_mood()
        self.__mbti = self.get_random_mbti()
        self.__situation = self.get_random_market_booth()
        self.__dialog_intro = self.get_random_greeting()
        self.__liked_words = self.get_random_likes()    # list of {"word": str, "points": int}
        self.__banned_words = self.get_random_dislikes(self.__liked_words)  # same structure
        self.points = 12
        self.__summaries = []
        self.__turn = 0

    def get_prompt(self):
        liked_str = ", ".join(w["word"] for w in self.__liked_words)
        banned_str = ", ".join(w["word"] for w in self.__banned_words)
        return (
            f"Your name is {self.__name}. You are an alien. Your mood is {self.__mood} and "
            f"you're an {self.__mbti}. You work as a {self.__situation[0]}, and you are situated in a "
            f"booth at a market where you are selling {self.__situation[1]}. "
            f"You enjoy {liked_str}. "
            f"You hate {banned_str}. "
            f"You have a maximum dialog of 5 responses before you want to end the conversation. "
            f"Your greeting is \"{self.__dialog_intro}\". I am looking to invite you "
            f"to the grand opening for my restaurant, but you don't know that yet. All you "
            f"know is that I approached your booth."
        )

    def get_points(self):
        return self.points

    def get_summaries(self):
        return self.__summaries

    def get_turn(self):
        return self.__turn

    def get_dict(self):
        return {
            "name": self.__name,
            "mood": self.__mood,
            "mbti": self.__mbti,
            "situation": self.__situation,
            "dialog_intro": self.__dialog_intro,
            "liked_words": self.__liked_words,
            "banned_words": self.__banned_words
        }

    def set_session(self, session):
        self.adk_session = session

    def add_summary(self, summary: str):
        self.__summaries.append(summary)

    def increment_turn(self):
        self.__turn += 1

    def get_random_name(self):
        return random.choice(self.alien_names)

    def get_random_mood(self):
        return random.choice(self.moods)

    def get_random_mbti(self):
        return random.choice(self.mbti)

    def get_random_market_booth(self):
        return random.choice(self.market_booths)

    def get_random_greeting(self):
        return random.choice(self.greetings)

    def get_random_likes(self):
        """Returns 20 unique liked words, each with a random point value 1-10."""
        chosen = random.sample(self.likes, 20)
        return [{"word": w, "points": random.randint(1, 10)} for w in chosen]

    def get_random_dislikes(self, likes):
        """Returns 20 unique disliked words (no overlap with likes), each with a random point value 1-10."""
        liked_words = {entry["word"] for entry in likes}
        pool = [w for w in self.likes if w not in liked_words]
        # If pool is too small, fall back to allowing overlap
        if len(pool) < 20:
            pool = self.likes
        chosen = random.sample(pool, min(20, len(pool)))
        return [{"word": w, "points": random.randint(1, 10)} for w in chosen]

    alien_names = [
        "Krag-Vark", "Lumina", "X'ylar", "Glip-Glop", "Xenophon", "Sshirra",
        "Grozznok", "Syllis", "Q-Tox", "Zorp", "Valerax", "Xis",
        "Thrax", "Aeryn", "Z'neer", "Poofer", "Thal'Darim", "Sslith",
        "Urk-Thul", "Oolala", "T'pau", "Blee-Bop", "Omnis", "Vess",
        "Zarkon", "Veea", "K'rk", "Squish", "Pyrax", "Hiss'r",
        "Krell", "Miri", "V'shaan", "Fizzle", "Solari", "Zzyzx",
        "Vorg", "Lloyo", "B'nal", "Womp", "Aurelius", "Fshh",
        "Blargen", "Esh-Na", "Xy'lo", "Zubble", "Krynn", "Sivv",
        "Drakk", "Inara", "J'kar", "Blip", "Zandros", "Xasha",
        "Ghor", "Nym", "Z'tah", "Noodle", "Xerxes", "Soren",
        "Mokk", "Kaelie", "V'Rox", "Gribble", "Aethelgard", "Suss",
        "Krax", "Yllos", "M'morp", "Zit", "Balthazarax", "Fwip",
        "Grond", "Lili-Va", "Xo", "Boop", "Kranston", "Vsh",
        "Zog", "Uuula", "Qun", "Splat", "Yar-Vax", "Zzz",
        "Krellik", "O-Oh", "V'Larr", "Wobble", "Talonis", "Slish",
        "Grak", "Iona", "K'Vok", "Pebble", "Ulduar", "Viss",
        "Zyn", "Meepo", "X'Nilo", "Gloop", "Vandor", "Skeer",
        "Rrax", "Kylo-Renish", "T'Mek", "Bleep", "Aethelred", "Xo'ru",
        "Vorg-Ath", "Lili", "Z'Yn", "Mop", "Kael-Thas", "Sshh",
        "Drog", "Yna", "Q'Ri", "Gloop-Gloop", "Thorn", "Vex"
    ]

    market_booths = [
        ["Farmer", "Bananas"],
        ["Beekeeper", "Wildflower Honey"],
        ["Baker", "Sourdough Bread"],
        ["Blacksmith", "Hand-forged Skillets"],
        ["Florist", "Sunflowers"],
        ["Potter", "Ceramic Mugs"],
        ["Carpenter", "Cedar Birdhouses"],
        ["Herbalist", "Dried Lavender"],
        ["Fisherman", "Smoked Salmon"],
        ["Cheesemaker", "Aged Cheddar"],
        ["Orchardist", "Cider Donuts"],
        ["Chocolatier", "Dark Chocolate Truffles"],
        ["Vintner", "Rose Wine"],
        ["Weaver", "Wool Blankets"],
        ["Butcher", "Grass-fed Jerky"],
        ["Soapmaker", "Eucalyptus Soap"],
        ["Gardener", "Heirloom Tomato Seeds"],
        ["Roaster", "Whole Bean Coffee"],
        ["Candlemaker", "Soy Wax Candles"],
        ["Calligrapher", "Hand-painted Cards"],
        ["Miller", "Stone-ground Grits"],
        ["Forager", "Chanterelle Mushrooms"],
        ["Sculptor", "Garden Gnomes"],
        ["Leatherworker", "Handmade Belts"],
        ["Linguist", "Rare Poetry Books"],
        ["Astrologer", "Star Charts"],
        ["Tea Sommelier", "Loose Leaf Oolong"],
        ["Jeweler", "Sea Glass Necklaces"],
        ["Cooper", "Oak Barrels"],
        ["Cartographer", "Vintage-style Maps"]
    ]

    mbti = [
        "entp", "intp", "esfj", "isfj", "estp", "istp", "enfj", "infj",
        "esfp", "isfp", "entj", "intj", "enfp", "infp", "estj", "istj"
    ]

    moods = [
        "Overexcited", "Hyper", "Frantic", "Anxious", "Restless",
        "Jittery", "Eager", "Rowdy", "Aggressive", "Panicked",
        "Chill", "Sleepy", "Lazy", "Melancholic", "Serene",
        "Dull", "Dreamy", "Lethargic", "Stoned", "Zoned-out",
        "Impatient", "Grumpy", "Cranky", "Bitter", "Sullen",
        "Bossy", "Stubborn", "Sarcastic", "Irritable", "Defiant",
        "Bubbly", "Cheerful", "Gentle", "Polite", "Curious",
        "Friendly", "Giddy", "Awestruck", "Playful", "Kind",
        "Shy", "Timid", "Awkward", "Nervous", "Quiet",
        "Fidgety", "Suspicious", "Hesitant", "Stoic", "Gloomy",
        "Serious", "Brainy", "Focused", "Puzzled", "Contemplative",
        "Formal", "Strict", "Arrogant", "Confident", "Mischievous"
    ]

    greetings = [
        "Hi, welcome to my booth!",
        "Good day, what's your name?",
        "Step closer, traveler, see what I've found.",
        "Are you buying, or just blocking the light?",
        "Greetings! Have you ever seen anything like this?",
        "You look like someone with a discerning eye.",
        "Move fast, I don't have all cycles to wait.",
        "Ho there! Care to trade?",
        "I haven't seen your species around here lately.",
        "A new face! Welcome, welcome.",
        "Stop! You won't find prices like these elsewhere.",
        "Looking for something special, or just wandering?",
        "Salutations, friend. What brings you to my stall?",
        "Careful where you step, and look with your eyes, not your claws.",
        "Interested in a bargain?",
        "Stay a moment! My goods are fresher than they look.",
        "I don't recognize your scent... are you from the inner rim?",
        "I hope you brought plenty of credits.",
        "Peace be with you. See anything you like?",
        "You there! You look like you need what I'm selling.",
        "The stars have brought you to the right place.",
        "I'm not in the mood for haggling today, just so you know.",
        "Come, look! Even a glimpse is free.",
        "May your journey be long, but your stop here be profitable.",
        "Don't just stare, make an offer!",
        "Ah, a customer at last.",
        "Do you seek knowledge, or just shiny things?",
        "Halt! You must see these before you pass.",
        "Is that a smile or a threat? Either way, welcome!",
        "Blessings upon your hive. What can I do for you?"
    ]

    likes = [
        "cooking", "zorx", "gymnastics", "music", "ruins", "navigation",
        "jazz", "fiction", "botany", "sports", "painting", "beekeeping",
        "weather", "fashion", "festivals", "mythology", "clockwork", "oceanography",
        "cinema", "photography", "exploration", "gambling", "metalwork", "conservation",
        "nostalgia", "comedy", "bioluminescence", "orchestras", "bargaining", "volcanoes",
        "astronomy", "traditions", "gardening", "velvet", "fermentation", "sculpture",
        "languages", "aviation", "beaches", "zorxball", "eating", "glassblowing",
        "fishing", "cartomancy", "taxidermy", "storms", "insects", "sand",
        "archery", "alchemy", "crystals", "herbalism", "pyrotechnics", "puppetry",
        "origami", "wrestling", "stargazing", "folklore", "brewing", "foraging",
        "weaving", "mapmaking", "fencing", "riddling", "divination", "falconry",
        "pottery", "tattooing", "juggling", "illusions", "clockmaking", "skincare"
    ]