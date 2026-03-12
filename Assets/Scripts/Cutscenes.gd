extends Control

var slides = [
	{
		"image": "res://Assets/Backgrounds/Cutscene1.jpg",
		"text": "You arrive on a strange alien world..."
	},
	{
		"image": "res://Assets/Backgrounds/Cutscene2.jpg",
		"text": "The market buzzes with life and color."
	},
	{
		"image": "res://Assets/Backgrounds/Cutscene3.jpg",
		"text": "Your mission: sell your product to the locals."
	}
]

var current_slide := 0

func _ready():
	show_slide(current_slide)

func _input(event):
	# Detect ANY key press
	if event.is_pressed() and event is InputEventKey:
		_on_next_pressed()

func show_slide(index):
	var slide = slides[index]
	$TextureRect.texture = load(slide["image"])
	$Label.text = slide["text"]

func _on_next_pressed():
	current_slide += 1

	if current_slide >= slides.size():
		get_tree().change_scene_to_file("res://Assets/Scenes/Map.tscn")
	else:
		show_slide(current_slide)
