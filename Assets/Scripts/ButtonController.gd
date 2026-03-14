extends Node

# ButtonController is an autoload. It cannot use relative $"../Button" paths
# because autoloads live at /root, not inside the Map scene.
# Instead, we wait for the Map scene's root node ("Control") to be added to the
# tree, then grab and connect the buttons dynamically.

var _buttons: Array = []

func _ready() -> void:
	get_tree().node_added.connect(_on_node_added)
	Dialogic.timeline_ended.connect(_on_timeline_ended)


func _on_node_added(node: Node) -> void:
	# The Map scene root is named "Control". Once it appears, bind buttons.
	if node.name == "Control" and _buttons.is_empty():
		call_deferred("_bind_buttons", node)


func _bind_buttons(map_root: Node) -> void:
	_buttons = [
		map_root.get_node_or_null("First_Button"),
		map_root.get_node_or_null("Second_Button"),
		map_root.get_node_or_null("Third_Button"),
		map_root.get_node_or_null("Fourth_Button"),
		map_root.get_node_or_null("Fifth_Button"),
		map_root.get_node_or_null("Sixth_Button"),
	]

	var methods = [
		"_on_first_button_pressed",
		"_on_second_button_pressed",
		"_on_third_button_pressed",
		"_on_fourth_button_pressed",
		"_on_fifth_button_pressed",
		"_on_sixth_button_pressed",
	]

	for i in range(_buttons.size()):
		var btn = _buttons[i]
		if btn == null:
			push_warning("ButtonController: button[%d] not found in scene." % i)
			continue
		if not btn.pressed.is_connected(Callable(self, methods[i])):
			btn.pressed.connect(Callable(self, methods[i]))
		# Hide pins for aliens already visited (e.g. after scene reload)
		if Global.button_flags[i]:
			btn.hide()


# ── button handlers ────────────────────────────────────────────────────────────

func _on_first_button_pressed()  -> void: _try_start(0)
func _on_second_button_pressed() -> void: _try_start(1)
func _on_third_button_pressed()  -> void: _try_start(2)
func _on_fourth_button_pressed() -> void: _try_start(3)
func _on_fifth_button_pressed()  -> void: _try_start(4)
func _on_sixth_button_pressed()  -> void: _try_start(5)


# ── logic ──────────────────────────────────────────────────────────────────────

func _try_start(alien_idx: int) -> void:
	# Block if already visited
	if Global.button_flags[alien_idx]:
		return

	Global.cur_alien_idx = alien_idx
	# start_alien_encounter is async; we await so button stays "busy"
	# until the timeline ends (timeline_ended fires and hides the pin).
	await DialogueController.start_alien_encounter(alien_idx)


func _on_timeline_ended() -> void:
	var idx: int = Global.cur_alien_idx
	if idx >= 0 and idx < _buttons.size():
		if Global.button_flags[idx] and _buttons[idx] != null:
			_buttons[idx].hide()
