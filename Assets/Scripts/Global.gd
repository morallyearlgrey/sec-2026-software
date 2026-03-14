extends Node
var dynamic_line: String = "123"
var player_input: String = ""
var num_turn: int = 0;

var button_flags = [false, false, false, false, false, false, false, false]

const BASE_URL = "http://localhost:8000"
const PLAYER_ID = "mcdiggity"

var qa_session_id: String = "";
var alien_session_id: String = "";


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
const Aliens = {
}

var cur_alien_idx = 0;

func get_alien(alien_id: int) -> Dictionary:
	return Aliens.get(alien_id, {})
