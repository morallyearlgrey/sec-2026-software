extends Node

func calculate_points(input: String, alien_id: int):
	var score = 0;
	
	var good_words: Dictionary = Global.get_alien(alien_id)["liked_words"].duplicate();
	
	var bad_words: Dictionary = Global.get_alien(alien_id)["banned_words"].duplicate();
		
	input = input.to_lower();
	var re = RegEx.new();
	re.compile("[^a-zA-Z0-9\\s]");
	input = re.sub(input, " ");

	var new_input = input.split(" ");
	
	for word in good_words.keys():
		if new_input.has(word.to_lower()):
			score += good_words[word];
			good_words.erase(word);
		
	for word in bad_words.keys():
		if new_input.has(word.to_lower()):
			score += bad_words[word];
			bad_words.erase(word);
		
	if(score<0):
		score=0;
		
	Global.get_alien(alien_id)["points"]=score;

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
