extends Control

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass

func _on_yes_button_pressed() -> void:
	get_tree().change_scene_to_file("res://Assets/Scenes/Map.tscn")

func _on_no_button_pressed() -> void:
	Dialogic.start("tutorial")
