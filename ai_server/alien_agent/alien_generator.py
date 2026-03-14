import random
from google.adk.runners import Runner

class Alien:
# Init  
    def __init__(self):
        self.__adk_session: Runner = ""
        self.__name: str = self.get_random_name()
        self.__mood: str = self.get_random_mood()
        self.__mbti: str = self.get_random_mbti()
        self.__situation: str = self.get_random_market_booth()
        self.__dialog_intro: str = self.get_random_greeting()
        self.__liked_words: str = self.get_random_likes()
        self.__banned_words: str = self.get_random_dislikes(self.__liked_words)
        self.__src: str = ""
        self.__points: int = 12
        self.__summaries: list[str] = []
        self.__turn: int = 0
        
# Methods
    def get_prompt(self)-> str:        
        return f"You name is {self.__name}. You are an alien. Your mood is {self.__mood} and \
you're an {self.__mbti}. You work as a {self.__situation[0]}, and you are situated in a \
booth at a market where you are selling {self.__situation[1]}. You enjoy {self.__liked_words[0]}, \
{self.__liked_words[0]}, and {self.__liked_words[1]}. You hate {self.__banned_words[0]}, {self.__banned_words[1]}, and \
{self.__banned_words[2]}. You have a maximum dialog of 5 responses before you want to end \
the conversation. Your greeting is \"{self.__dialog_intro}\". I am looking to invite you \
to the grand opening for my restaurant, but you don't know that yet. All you \
know is that I approached your booth."

    def alien_dict(self):
        alien_attributes = {
            "name": self.__name,
            "mood": self.__mood,
            "mbti": self.__mbti,
            "situation": self.__situation,
            "dialog intro": self.__dialog_intro,
            "liked words": self.__liked_words,
            "banned words": self.__banned_words,
        }
        
        alien_backend = {
            "src": self.__src,
            "points": self.__points,
            "summaries": self.__summaries,
            "turn": self.__turn
        }
        
        return {
            "alien attributes": alien_attributes,
            "alien backend": alien_backend
        }
                
    def increment_turn(self) -> None:
        self.__turn += 1


# Getters/Setters
    def get_points(self) -> int:
        return self.__points
    
    def get_summaries(self) -> list[str]:
        return self.__summaries
    
    def get_id(self) -> str:
        return self.__id
    
    def get_turn(self) -> int:
        return self.__turn

    def set_session(self, session) -> str:
        self.__adk_session = session

    def add_summary(self, summary: str) -> None:
        self.__summaries.append(summary)

# Init randoms
    def get_random_name(self) -> str:
        rand = random.randint(0, len(self.alien_names) - 1)
        return self.alien_names[rand]

    def get_random_mood(self) -> str:
        rand = random.randint(0, len(self.moods) - 1)
        return self.moods[rand]
            
    def get_random_mbti(self) -> str:
        rand = random.randint(0, len(self.mbti) - 1)
        return self.mbti[rand]

    def get_random_market_booth(self) -> str:    
        rand = random.randint(0, len(self.market_booths) - 1)
        return self.market_booths[rand]

    def get_random_greeting(self) -> str:
        rand = random.randint(0, len(self.greetings) - 1)
        return self.greetings[rand]
    
    def get_random_likes(self) -> list[str]:
        likes = []
        
        for i in range(3):
            rand = random.randint(0, len(self.likes) - 1)

            while self.likes[rand] in likes:
                rand = random.randint(0, len(self.likes) - 1)

            likes.append(self.likes[rand])
            
        return likes
    
    def get_random_dislikes(self, likes) -> list[str]:
        dislikes = []
        
        for i in range(3):
            rand = random.randint(0, len(self.likes) - 1)
            
            while self.likes[rand] in likes and self.likes[rand] in dislikes:
                rand = random.randint(0, len(self.likes) - 1)
                
            dislikes.append(self.likes[rand])
        
        return dislikes

    alien_names: list[str] = [
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

    market_booths: list[list[str]] = [
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

    mbti: list[str] = [
        "entp", "intp", "esfj", "isfj", "estp", "istp", "enfj", "infj", 
        "esfp", "isfp", "entj", "intj", "enfp", "infp", "estj", "istj"
    ]

    moods: list[str] = [
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

    greetings: list[str] = [
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
    
    likes: list[str] = [
        "culinary arts",
        "the game zorx",
        "rhythmic gymnastics",
        "street food",
        "architectural ruins",
        "maritime navigation",
        "experimental jazz",
        "speculative fiction",
        "terrestrial botany",
        "competitive sports",
        "abstract painting",
        "beekeeping",
        "meteorological phenomena",
        "haute couture",
        "amusement parks",
        "folk mythology",
        "mechanical watches",
        "oceanography",
        "cinematography",
        "analog photography",
        "urban exploration",
        "board game marathons",
        "heavy metal subcultures",
        "wildlife conservation",
        "the concept of nostalgia",
        "stand-up comedy",
        "bioluminescence",
        "symphonic orchestras",
        "bazaar shopping",
        "geothermal springs",
        "amateur astronomy",
        "holiday traditions",
        "landscape gardening",
        "the velvet industry",
        "fermentation science",
        "sculpture galleries",
        "ancient languages",
        "aviation history",
        "beach culture",
        "the zorxian world championships"
    ]