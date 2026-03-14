extends Node

func _ready() -> void:
	Dialogic.start("tutorial_alien")
	
func _process(delta: float) -> void:
	if Global.cur_alien_idx > 5:
		get_tree().change_scene_to_file("res://Assets/Scenes/ExitScreen.tscn")

	
func _on_first_button_pressed() -> void:
	if Global.button_flags[0] == true:
		pass
	else:
		Dialogic.start("Timelines/first_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[0] = true

func _on_second_button_pressed() -> void:
	if Global.button_flags[1] == true:
		pass
	else:
		Dialogic.start("second_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[1] = true

func _on_third_button_pressed() -> void:
	if Global.button_flags[2] == true:
		pass
	else:
		Dialogic.start("third_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[2] = true

func _on_fourth_button_pressed() -> void:
	if Global.button_flags[3] == true:
		pass
	else:
		Dialogic.start("fourth_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[3] = true

func _on_fifth_button_pressed() -> void:
	if Global.button_flags[4] == true:
		pass
	else:
		Dialogic.start("fifth_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[4] = true

func _on_sixth_button_pressed() -> void:
	if Global.button_flags[5] == true:
		pass
	else:
		Dialogic.start("sixth_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[5] = true
