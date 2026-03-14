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

var Aliens: Dictionary = {}
var cur_alien_idx: int = 0

func get_alien(alien_id: int) -> Dictionary:
	return Aliens.get(alien_id, {})

func register_alien(alien_id: int, data: Dictionary) -> void:
	data["index"]           = alien_id
	data["num_turns"]       = 5
	data["happiness_meter"] = 0.0
	data["points"]          = 0
	data["visited"]         = false
	data["alien_response"]  = data.get("greeting", "")
	# Use the McDoogles logo as the portrait for every alien
	data["src"]             = "res://Assets/Icons/Logo.png"
	Aliens[alien_id]        = data

	Dialogic.VAR.set("alien_name",     data.get("name", "???"))
	Dialogic.VAR.set("alien_image",    data["src"])
	Dialogic.VAR.set("alien_response", data["alien_response"])
	Dialogic.VAR.set("player_input",   "")
	Dialogic.VAR.set("turn_valid",     false)
	Dialogic.VAR.set("qa_reason",      "")
