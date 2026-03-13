import re

extends Node

static func calculate_points(input: String, alien_id: int):
	var good_words = Aliens[alien_id]["liked_words"];
	
	re.sub(r'[^a-zA-Z0-9\s]', ' ', input);
	new_input = input.split(" ");
	
	

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
