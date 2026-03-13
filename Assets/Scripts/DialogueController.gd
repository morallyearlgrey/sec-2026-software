extends Node

func dynamic_dialogue() -> void:
	var lines = [
		"Fresh moonberries!",
		"Careful, those glow.",
        "Straight from the asteroid farms."
	]
	Global.dynamic_line = lines[Global.i]
	Global.i = Global.i + 1
	
func static_dialogue():
	Global.set_variable("dynamic_line", "Fresh alien fruit!")
