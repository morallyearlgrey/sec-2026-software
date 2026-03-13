extends Node

# index, int
# name, string
# mood, string
# mbti, string
# situation, string arr
# dialogue_intro, string
# liked_words, string-int dict
# banned_words, string-int dict
# happiness_meter, float
# src, string
# points, int
const Aliens = {
}

func get_alien(alien_id: String) -> Dictionary:
	return alien_state.get(alien_id, {})

func add_points(alien_id: String, amount: int):
	if alien_state.has(alien_id):
		alien_state[alien_id]["points"] += amount

	

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
