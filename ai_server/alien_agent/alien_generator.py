import random

class AlienGenerator:
    
    def __init__(self):
        print(self.get_prompt())

    def get_prompt(self):
        name = self.get_random_name()
        mood = self.get_random_mood()
        mbti = self.get_random_mbti()
        situation = self.get_random_market_booth()
        greeting = self.get_random_greeting()
        return f"You name is {name}. You are an alien. Your mood is {mood} \
and you're an {mbti}. You work as a {situation[0]}, and you are \
situated in a booth at a market where you are selling \
{situation[1]}. You have a maximum dialog of 5 responses before \
you want to end the conversation. Your greeting is \"{greeting}\". \
I am looking to invite you to the grand opening for my \
restaurant, but you don't know that yet. All you know is that I \
approached your booth."

    def get_random_name(self):
        rand = random.randint(0, len(self.alien_names))
        return self.alien_names[rand]


    def get_random_mood(self):
        rand = random.randint(0, len(self.moods))
        return self.moods[rand]
            
    def get_random_mbti(self):
        rand = random.randint(0, len(self.mbti))
        return self.mbti[rand]

    def get_random_market_booth(self):    
        rand = random.randint(0, len(self.market_booths))
        return self.market_booths[rand]

    def get_random_greeting(self):
        rand = random.randint(0, len(self.greetings))
        return self.greetings[rand]

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