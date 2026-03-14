extends Node

# calculate_points takes the QA summary (plain English sentence) and the alien
# index, matches liked/banned words, and accumulates a score on the alien.
func calculate_points(input: String, alien_id: int) -> void:
	var alien: Dictionary = Global.get_alien(alien_id)
	if alien.is_empty():
		return

	var score: int = 0

	var good_words: Dictionary = alien.get("liked_words",  {}).duplicate()
	var bad_words:  Dictionary = alien.get("banned_words", {}).duplicate()

	# Normalise: lowercase, strip punctuation
	input = input.to_lower()
	var re = RegEx.new()
	re.compile("[^a-zA-Z0-9\\s]")
	input = re.sub(input, " ")

	var words: PackedStringArray = input.split(" ")

	for word in good_words.keys():
		if words.has(word.to_lower()):
			score += good_words[word]

	for word in bad_words.keys():
		if words.has(word.to_lower()):
			score += bad_words[word]   # these are already negative

	score = max(score, 0)

	# Accumulate (don't overwrite — add to running total)
	Global.Aliens[alien_id]["points"] = alien.get("points", 0) + score

func _ready() -> void:
	pass
