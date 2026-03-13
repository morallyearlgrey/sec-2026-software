extends Node

func calculate_points(input: String, alien_id: int):
	var score = 0;
	
	var good_words = Aliens.get_alien(alien_id)["liked_words"];
	var bad_words = Aliens.get_alien(alien_id)["banned_words"];
		
	input = input.to_lower();
	var re = RegEx.new();
	re.compile("[^a-zA-Z0-9\\s]");
	input = re.sub(input, " ");

	var new_input = input.split(" ");
	
	for word in good_words.keys():
		if word.to_lower()==new_input:
			score += good_words[word];
		
	for word in bad_words.keys():
		if word.to_lower()==new_input:
			score += good_words[word];
		
	if(score<0):
		score=0;
		
	Aliens.get_alien(alien_id)["points"]=score;

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
