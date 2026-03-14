extends Node
var dynamic_line: String = "123"
var player_input: String = ""

#var button_flags = [false, false, false, false, false, false, false, false]

const BASE_URL = "http://localhost:8000"
const PLAYER_ID = "mcdiggity"

# index, int
# name, string
# mood, string
# mbti, string
# situation, string arr
# dialogue_intro, string
# liked_words, string-int dict
# num_turns
# banned_words, string-int dict
# happiness_meter, float
# src, string
# points, int
var aliens: Array = []

var qa_session_id:    String = ""
var alien_session_id: String = ""
var cur_alien_idx = 0;

func get_alien(idx: int) -> Dictionary:
	if idx >= 0 and idx < aliens.size():
		return aliens[idx]
	return {}
	
func set_alien_field(idx: int, key: String, value) -> void:
	if idx >= 0 and idx < aliens.size():
		aliens[idx][key] = value
		
func mark_visited(idx: int) -> void:
	set_alien_field(idx, "visited", true)
	
func total_points() -> int:
	var sum = 0
	for a in aliens:
		sum += a.get("points", 0)
	return sum
