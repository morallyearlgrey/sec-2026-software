import random
import sys
import os

# Ensure the directory containing this file is always on sys.path
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)


class AlienGenerator:

    def __init__(self):
        self.name      = self.get_random_name()
        self.mood      = self.get_random_mood()
        self.mbti      = self.get_random_mbti()
        self.situation = self.get_random_market_booth()
        self.greeting  = self.get_random_greeting()
        self.likes     = self.get_random_likes()
        self.dislikes  = self.get_random_dislikes(self.likes)


    def get_prompt(self):
        return (
            f"You name is {self.name}. You are an alien. Your mood is {self.mood} and "
            f"you're an {self.mbti}. You work as a {self.situation[0]}, and you are situated in a "
            f"booth at a market where you are selling {self.situation[1]}. You enjoy {self.likes[0]}, "
            f"{self.likes[1]}, and {self.likes[2]}. You hate {self.dislikes[0]}, {self.dislikes[1]}, and "
            f"{self.dislikes[2]}. You have a maximum dialog of 5 responses before you want to end "
            f"the conversation. Your greeting is \"{self.greeting}\". I am looking to invite you "
            f"to the grand opening for my restaurant, but you don't know that yet. All you "
            f"know is that I approached your booth."
        )

    def get_dict(self):
        name      = self.get_random_name()
        mood      = self.get_random_mood()
        mbti      = self.get_random_mbti()
        situation = self.get_random_market_booth()
        likes     = self.get_random_likes()
        dislikes  = self.get_random_dislikes(likes)
        greeting  = self.get_random_greeting(likes, dislikes)

        return {
            "name":      name,
            "mood":      mood,
            "mbti":      mbti,
            "situation": situation,
            "likes":     likes,
            "dislikes":  dislikes,
            "greeting":  greeting,
            "points": 0,
            "src": "",
        }

    def get_random_name(self):
        return random.choice(self.alien_names)

    def get_random_mood(self):
        return random.choice(self.moods)

    def get_random_mbti(self):
        return random.choice(self.mbti)

    def get_random_market_booth(self):
        return random.choice(self.market_booths)

    def get_random_likes(self):
        likes = []
        
        for i in range(3):
            rand = random.randint(0, len(self.likes) - 1)
            
            while self.likes[rand] in likes:
                rand = random.randint(0, len(self.likes) - 1)
                
            likes.append({
                "like": self.likes[rand],
                "weight": i * 2
            })
            
        return likes

    def get_random_dislikes(self, likes):
        dislikes = []
        
        for i in range(3):
            rand = random.randint(0, len(self.likes) - 1)
            
            while self.likes[rand] in likes or self.likes[rand] in dislikes:
                rand = random.randint(0, len(self.likes) - 1)
                
            likes.append({
                "dislike": self.likes[rand],
                "weight": i * -2
            })
            
        return dislikes
        
    def get_random_greeting(self):
        greeting = random.choice(self.greetings)
        f"[You are now talking to {self.name}. After doing some research, you "
        f"have learned that they like {self.likes[0]}, {self.likes[1]}, and "
        f"{self.likes[2]}. You have also learned that they hate "
        f"{self.dislikes[0]}, {self.dislikes[1]}, and {self.dislikes[2]}. "
        f"You may use this information to appeal to their values.]\n\""
        f"{greeting}\""

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