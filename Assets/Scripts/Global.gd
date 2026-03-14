extends Node

var dynamic_line: String = ""
var player_input: String = ""
var num_turn: int = 0

# 6 aliens, indices 0–5
var button_flags = [false, false, false, false, false, false]

const BASE_URL = "http://localhost:8000"
const PLAYER_ID = "mcdiggity"

var qa_session_id: String = ""
var alien_session_id: String = ""

# Alien data structure populated at runtime by generate_alien().
# Keys per entry:
#   index          int
#   name           String
#   mood           String
#   mbti           String
#   situation      Array[String]  [job, item]
#   greeting       String
#   likes          Array[String]
#   dislikes       Array[String]
#   dialogue_intro String         (the alien's opening line)
#   alien_response String         (the alien's latest reply, updated each turn)
#   liked_words    Dictionary     word -> point value
#   banned_words   Dictionary     word -> point value (negative)
#   num_turns      int            (always 5)
#   happiness_meter float
#   src            String         image path
#   points         int
#   visited        bool
var Aliens: Dictionary = {}

var cur_alien_idx: int = 0

func get_alien(alien_id: int) -> Dictionary:
	return Aliens.get(alien_id, {})

# Called by DialogueController after generate_alien() returns data.
# Stores it in Aliens and sets Dialogic vars so the timeline can read them.
func register_alien(alien_id: int, data: Dictionary) -> void:
	data["index"] = alien_id
	data["num_turns"] = 5
	data["happiness_meter"] = 0.0
	data["points"] = 0
	data["visited"] = false
	data["alien_response"] = data.get("greeting", "")
	# Assign a random sprite from alien1..alien6
	data["src"] = "res://Assets/Characters/Images/alien%d.png" % ((alien_id % 6) + 1)
	Aliens[alien_id] = data

	# Push into Dialogic globals so the timeline can read them immediately.
	Dialogic.VAR.set("alien_name", data.get("name", "???"))
	Dialogic.VAR.set("alien_image", data["src"])
	Dialogic.VAR.set("alien_response", data["alien_response"])
	Dialogic.VAR.set("player_input", "")
	Dialogic.VAR.set("turn_valid", false)
	Dialogic.VAR.set("qa_reason", "")
