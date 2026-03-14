extends Node

# ── constants ──────────────────────────────────────────────────────────────────
const MAX_TURNS     = 5
const INPUT_TIMEOUT = 30.0

# ── state ──────────────────────────────────────────────────────────────────────
var _alien_idx: int   = -1
var _turn:      int   = 0
var _timer:     Timer = null
var _input_box: Node = null   # reference to the custom LineEdit overlay

# ── signals ────────────────────────────────────────────────────────────────────
# Emitted when the controller finishes async work so the timeline can resume.
signal turn_resolved

# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC — called by ButtonController
# ══════════════════════════════════════════════════════════════════════════════

func start_alien_encounter(alien_idx: int) -> void:
	_alien_idx = alien_idx
	_turn      = 0

	# 1. Generate alien
	var alien_data: Dictionary = await APIClient.generate_alien()
	if alien_data.has("error") or alien_data.is_empty():
		push_error("DialogueController: generate_alien failed")
		return

	# 2. Create sessions
	Global.alien_session_id = await APIClient.create_session("alien_agent")
	Global.qa_session_id    = await APIClient.create_session("qa_agent")

	# 3. Register + set Dialogic vars
	Global.register_alien(alien_idx, alien_data)
	Global.cur_alien_idx = alien_idx

	# 4. Get opening line from alien agent
	var intro: String = await APIClient.run_alien(
		Global.alien_session_id,
		alien_data.get("greeting", "Hello."),
		"(conversation start)"
	)
	if intro == "":
		intro = alien_data.get("greeting", "Hello.")

	Global.Aliens[alien_idx]["alien_response"] = intro
	Dialogic.VAR.set("alien_response", intro)
	Dialogic.VAR.set("alien_name",     alien_data.get("name", "???"))
	Dialogic.VAR.set("alien_image",    Global.Aliens[alien_idx]["src"])
	Dialogic.VAR.set("player_input",   "")
	Dialogic.VAR.set("turn_valid",     false)
	Dialogic.VAR.set("qa_reason",      "")
	Dialogic.VAR.set("turn_number",    0)
	Dialogic.VAR.set("game_over",      false)
	Dialogic.VAR.set("timed_out",      false)

	# 5. Start timeline
	Dialogic.start("alien_encounter")


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC — called from timeline via `do DialogueController.show_input()`
# These must be non-async (no await) because Dialogic's `do` is synchronous.
# ══════════════════════════════════════════════════════════════════════════════

## Called by the timeline to show the input box and start the 30s timer.
## The timeline immediately continues past this `do` call, then hits a
## `wait_for_signal` event that blocks until `turn_resolved` fires.
func show_input() -> void:
	Dialogic.VAR.set("player_input", "")
	Dialogic.VAR.set("timed_out",    false)
	_show_input_overlay()
	_start_timer()


## Called by the input box's Submit button (connected in _show_input_overlay).
func on_player_submitted() -> void:
	_stop_timer()
	var text: String = _get_input_text()
	_hide_input_overlay()
	# Kick off the async pipeline without awaiting it here —
	# _process_turn will emit turn_resolved when done.
	_process_turn.call_deferred(text)


# ══════════════════════════════════════════════════════════════════════════════
# PRIVATE — timer
# ══════════════════════════════════════════════════════════════════════════════

func _start_timer() -> void:
	if _timer == null:
		_timer = Timer.new()
		_timer.one_shot = true
		add_child(_timer)
		_timer.timeout.connect(_on_timeout)
	_timer.start(INPUT_TIMEOUT)


func _stop_timer() -> void:
	if _timer != null and not _timer.is_stopped():
		_timer.stop()


func _on_timeout() -> void:
	var text: String = _get_input_text()
	_hide_input_overlay()
	Dialogic.VAR.set("timed_out", true)
	_process_turn.call_deferred(text)


# ══════════════════════════════════════════════════════════════════════════════
# PRIVATE — input overlay
# We build a simple LineEdit + Button overlay and attach it to the Dialogic
# layout so it sits on top of the textbox.
# ══════════════════════════════════════════════════════════════════════════════

func _show_input_overlay() -> void:
	if _input_box != null:
		_input_box.show()

		var le: LineEdit = _input_box.get_node("PanelContainer/HBoxContainer/LineEdit")
		if le:
			le.text = ""
			le.grab_focus()

		return

	# Build the overlay once
	var canvas := CanvasLayer.new()
	canvas.layer = 10
	canvas.name  = "InputOverlay"
	get_tree().root.add_child(canvas)

	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	panel.offset_top    = -160.0
	panel.offset_bottom = -10.0
	panel.offset_left   = 160.0
	panel.offset_right  = -160.0
	canvas.add_child(panel)

	var hbox := HBoxContainer.new()
	hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.add_child(hbox)

	var le := LineEdit.new()
	le.name                     = "LineEdit"
	le.placeholder_text         = "Type your response here… (30 seconds)"
	le.size_flags_horizontal    = Control.SIZE_EXPAND_FILL
	le.custom_minimum_size      = Vector2(0, 60)
	hbox.add_child(le)

	var btn := Button.new()
	btn.text                 = "Submit"
	btn.custom_minimum_size  = Vector2(140, 60)
	hbox.add_child(btn)

	# Connect submit via button click AND Enter key
	btn.pressed.connect(on_player_submitted)
	le.text_submitted.connect(func(_t): on_player_submitted())

	_input_box = canvas
	le.grab_focus()


func _hide_input_overlay() -> void:
	if _input_box != null:
		_input_box.hide()


func _get_input_text() -> String:
	if _input_box == null:
		return Dialogic.VAR.get("player_input")
	var panel = _input_box.get_child(0)           # PanelContainer
	var hbox  = panel.get_child(0)                # HBoxContainer
	var le: LineEdit = hbox.get_child(0)          # LineEdit
	return le.text.strip_edges()


# ══════════════════════════════════════════════════════════════════════════════
# PRIVATE — core pipeline (async, driven by call_deferred from show_input path)
# ══════════════════════════════════════════════════════════════════════════════

func _process_turn(player_text: String) -> void:
	var alien_line: String = Global.Aliens[_alien_idx].get("alien_response", "")

	# ── QA ──────────────────────────────────────────────────────────────────
	var qa: Dictionary = await APIClient.run_qa(
		Global.qa_session_id, alien_line, player_text
	)

	var is_valid: bool   = qa.get("validity", false)
	var reason:   String = qa.get("reason",   "That response wasn't quite right.")
	var summary:  String = qa.get("summary",  player_text)

	if not is_valid:
		Dialogic.VAR.set("turn_valid", false)
		Dialogic.VAR.set("qa_reason",  reason)
		# Resume the timeline (it will show the rejection line, then loop back
		# to show_input which re-shows the overlay)
		emit_signal("turn_resolved")
		return

	# ── Valid turn ───────────────────────────────────────────────────────────
	_turn += 1
	Dialogic.VAR.set("turn_valid",   true)
	Dialogic.VAR.set("turn_number",  _turn)
	Dialogic.VAR.set("qa_reason",    "")

	PointCalculator.calculate_points(summary, _alien_idx)

	if _turn >= MAX_TURNS:
		Global.Aliens[_alien_idx]["visited"] = true
		Global.button_flags[_alien_idx]      = true
		Dialogic.VAR.set("game_over", true)
		emit_signal("turn_resolved")
		return

	# ── Alien responds ───────────────────────────────────────────────────────
	var reply: String = await APIClient.run_alien(
		Global.alien_session_id, alien_line, summary
	)
	if reply == "":
		reply = "Hmm… interesting."

	Global.Aliens[_alien_idx]["alien_response"] = reply
	Dialogic.VAR.set("alien_response", reply)

	emit_signal("turn_resolved")
