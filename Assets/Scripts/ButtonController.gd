extends Node

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
		Dialogic.start("Timelines/first_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[1] = true

func _on_third_button_pressed() -> void:
	if Global.button_flags[2] == true:
		pass
	else:
		Dialogic.start("Timelines/first_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[2] = true

func _on_fourth_button_pressed() -> void:
	if Global.button_flags[3] == true:
		pass
	else:
		Dialogic.start("Timelines/first_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[3] = true

func _on_fifth_button_pressed() -> void:
	if Global.button_flags[4] == true:
		pass
	else:
		Dialogic.start("Timelines/first_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[4] = true

func _on_sixth_button_pressed() -> void:
	if Global.button_flags[5] == true:
		pass
	else:
		Dialogic.start("Timelines/first_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[5] = true

func _on_seventh_button_pressed() -> void:
	if Global.button_flags[6] == true:
		pass
	else:
		Dialogic.start("Timelines/first_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[6] = true

func _on_eighth_button_pressed() -> void:
	if Global.button_flags[7] == true:
		pass
	else:
		Dialogic.start("Timelines/first_alien")
		Global.cur_alien_idx = Global.cur_alien_idx + 1
		Global.button_flags[7] = true
