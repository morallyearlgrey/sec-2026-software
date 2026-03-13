import re

extends Node

func calculate_points(input: String, alien_id: String) -> int:
	var score = 0
	
	var clean_input = ""
	for ch in input:
		if ch.to_upper() != ch.to_lower() or ch == " ":  
			clean_input += ch.to_lower()
		else:
			clean_input += " "
	
	var words = clean_input.split(" ", false) 
	var good_words = Aliens.get_alien(alien_id)["liked_words"].duplicate()
	var bad_words = Aliens.get_alien(alien_id)["banned_words"].duplicate()
	
	for word in words:
		if good_words.has(word):
			score += good_words[word]
			good_words.erase(word) 
		
		if bad_words.has(word):
			bad_words.erase(word)
	
	return max(score, 0) 


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
