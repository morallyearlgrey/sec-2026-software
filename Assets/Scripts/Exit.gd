extends Control

func _ready() -> void:
	$AnimationPlayer.play("ending")

var holder_scene = preload("res://Assets/Scenes/SpriteHolder.tscn")

func populate_characters():
	var box = $Frame/CharacterBox

	# Clear old holders
	for child in box.get_children():
		child.queue_free()
		
	var holder = holder_scene.instantiate()
	var sprite = holder.get_node("Sprite2D")
	sprite.texture = load("res://Assets/Characters/MainCharacter.png")
	box.add_child(holder)

	for i in range(3):
		holder = holder_scene.instantiate()
		sprite = holder.get_node("Sprite2D")
		sprite.texture = load("res://Assets/Characters/images/alien_3.png")
		box.add_child(holder)

	## Loop through all aliens in the dictionary
	#for alien_id in Aliens.keys():
		#var alien = Global.get_alien(alien_id)
#
		## Skip invalid or low-score aliens
		#if alien.is_empty():
			#continue
		#if alien.points < 8:
			#continue
#
		## Create sprite for this alien
		#var sprite = Sprite2D.new()
		#sprite.texture = load(alien.src)
		#box.add_child(sprite)

func _on_restart_button_pressed() -> void:
	get_tree().change_scene_to_file("res://Assets/Scenes/TitleScreen.tscn")
