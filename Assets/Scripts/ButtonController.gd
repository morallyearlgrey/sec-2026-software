extends Node


func _on_first_button_pressed() -> void:
	Dialogic.start("first_alien")


func _on_second_button_pressed() -> void:
	Dialogic.start("second_alien")
