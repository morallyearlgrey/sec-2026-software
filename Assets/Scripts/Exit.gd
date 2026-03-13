extends Control

func _ready() -> void:
	# Start a loop displaying each alien walking into a building.
	# Then show rolling statistic credits showing aliens, happiness, etc.
	pass

func _on_restart_button_pressed() -> void:
	get_tree().change_scene_to_file("res://Assets/Scenes/TitleScreen.tscn")
