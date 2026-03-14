extends Node

const MAX_TURNS     = 5
const INPUT_TIMEOUT = 30.0

var _alien_idx:       int     = -1
var _turn:            int     = 0
var _time_left:       float   = INPUT_TIMEOUT

# Timer node — ticks every second so we can update the countdown label
var _timer:           Timer   = null

# Direct references to overlay nodes — set once when overlay is first built
var _overlay_canvas:  Node    = null   # CanvasLayer
var _line_edit:       LineEdit  = null
var _countdown_label: Label     = null
var _speaker_label:   Label     = null

signal turn_resolved

# ══════════════════════════════════════════════════════════════════════════════
# Entry point — called by ButtonController
# ══════════════════════════════════════════════════════════════════════════════

func start_alien_encounter(alien_idx: int) -> void:
	_alien_idx = alien_idx
	_turn      = 0

	var alien_data: Dictionary = await APIClient.generate_alien()
	if alien_data.has("error") or alien_data.is_empty():
		push_error("DialogueController: generate_alien failed")
		return

	Global.alien_session_id = await APIClient.create_session("alien_agent")
	Global.qa_session_id    = await APIClient.create_session("qa_agent")

	Global.register_alien(alien_idx, alien_data)
	Global.cur_alien_idx = alien_idx

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

	Dialogic.start("alien_encounter")


# ══════════════════════════════════════════════════════════════════════════════
# Called synchronously from timeline:  do DialogueController.show_input()
# Then timeline immediately hits:      signal DialogueController turn_resolved
# which blocks until _process_turn() emits the signal.
# ══════════════════════════════════════════════════════════════════════════════

func show_input() -> void:
	Dialogic.VAR.set("player_input", "")
	Dialogic.VAR.set("timed_out",    false)
	_build_overlay_if_needed()
	# Update the speaker label with the current alien's name
	if _speaker_label:
		_speaker_label.text = str(Dialogic.VAR.get("alien_name")) + " is waiting…"
	# Show and reset
	_overlay_canvas.show()
	_line_edit.text = ""
	_line_edit.grab_focus()
	_start_countdown()


# ══════════════════════════════════════════════════════════════════════════════
# Timer — ticks every second, updates countdown label
# ══════════════════════════════════════════════════════════════════════════════

func _start_countdown() -> void:
	_time_left = INPUT_TIMEOUT
	_update_countdown()
	if _timer == null:
		_timer = Timer.new()
		_timer.wait_time = 1.0
		_timer.one_shot  = false
		add_child(_timer)
		_timer.timeout.connect(_on_tick)
	_timer.start()


func _stop_countdown() -> void:
	if _timer != null:
		_timer.stop()


func _on_tick() -> void:
	_time_left -= 1.0
	_update_countdown()
	if _time_left <= 0.0:
		_stop_countdown()
		var text := _line_edit.text.strip_edges() if _line_edit else ""
		_overlay_canvas.hide()
		Dialogic.VAR.set("timed_out", true)
		_process_turn.call_deferred(text)


func _update_countdown() -> void:
	if _countdown_label:
		_countdown_label.text = str(int(max(_time_left, 0)))


# ══════════════════════════════════════════════════════════════════════════════
# Overlay — built once, reused every turn
# CanvasLayer at layer 200 so it's always above Dialogic (layer ~100)
#
# Layout:
#   CanvasLayer (200)
#     MarginContainer  (full screen, bottom-anchored strip)
#       VBoxContainer
#         ├─ HBoxContainer
#         │    ├─ Label  "AlienName is waiting…"   (expands)
#         │    └─ Panel  countdown circle
#         │         └─ Label  "30"
#         └─ HBoxContainer
#              ├─ LineEdit  (expands)
#              └─ Button  "Submit"
# ══════════════════════════════════════════════════════════════════════════════

func _build_overlay_if_needed() -> void:
	if _overlay_canvas != null:
		return   # already built

	# ── CanvasLayer ──────────────────────────────────────────────────────────
	var canvas := CanvasLayer.new()
	canvas.layer = 200
	canvas.name  = "InputOverlay"
	get_tree().root.add_child(canvas)
	_overlay_canvas = canvas

	# ── Root control: pin a tall strip to the bottom of the screen ───────────
	var root_ctrl := Control.new()
	root_ctrl.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	root_ctrl.offset_top    = -200.0
	root_ctrl.offset_bottom = 0.0
	root_ctrl.offset_left   = 0.0
	root_ctrl.offset_right  = 0.0
	canvas.add_child(root_ctrl)

	# Semi-transparent dark background for readability
	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.0, 0.0, 0.0, 0.72)
	root_ctrl.add_child(bg)

	# ── VBox holds both rows ─────────────────────────────────────────────────
	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	vbox.offset_left   = 24.0
	vbox.offset_right  = -24.0
	vbox.offset_top    = 12.0
	vbox.offset_bottom = -12.0
	vbox.add_theme_constant_override("separation", 10)
	root_ctrl.add_child(vbox)

	# ── Top row: speaker name + countdown ────────────────────────────────────
	var top_row := HBoxContainer.new()
	top_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top_row.add_theme_constant_override("separation", 16)
	vbox.add_child(top_row)

	var speaker := Label.new()
	speaker.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	speaker.add_theme_font_size_override("font_size", 30)
	speaker.add_theme_color_override("font_color", Color(0.9, 0.85, 1.0))
	speaker.text = "Alien is waiting…"
	top_row.add_child(speaker)
	_speaker_label = speaker

	# Countdown box
	var cd_panel := PanelContainer.new()
	cd_panel.custom_minimum_size = Vector2(80, 80)
	top_row.add_child(cd_panel)

	var cd_lbl := Label.new()
	cd_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cd_lbl.vertical_alignment   = VERTICAL_ALIGNMENT_CENTER
	cd_lbl.add_theme_font_size_override("font_size", 44)
	cd_lbl.add_theme_color_override("font_color", Color(1.0, 0.35, 0.2))
	cd_lbl.text = "30"
	cd_panel.add_child(cd_lbl)
	_countdown_label = cd_lbl

	# ── Bottom row: text input + submit button ────────────────────────────────
	var bot_row := HBoxContainer.new()
	bot_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bot_row.add_theme_constant_override("separation", 12)
	vbox.add_child(bot_row)

	var le := LineEdit.new()
	le.placeholder_text      = "Type your response here…"
	le.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	le.custom_minimum_size   = Vector2(0, 64)
	le.add_theme_font_size_override("font_size", 28)
	bot_row.add_child(le)
	_line_edit = le

	var btn := Button.new()
	btn.text               = "Submit"
	btn.custom_minimum_size = Vector2(160, 64)
	btn.add_theme_font_size_override("font_size", 28)
	bot_row.add_child(btn)

	btn.pressed.connect(_on_submit)
	le.text_submitted.connect(func(_t): _on_submit())


func _on_submit() -> void:
	_stop_countdown()
	var text := _line_edit.text.strip_edges() if _line_edit else ""
	_overlay_canvas.hide()
	_process_turn.call_deferred(text)


# ══════════════════════════════════════════════════════════════════════════════
# Core async pipeline — runs after player submits or timer expires
# ══════════════════════════════════════════════════════════════════════════════

func _process_turn(player_text: String) -> void:
	var alien_line: String = Global.Aliens[_alien_idx].get("alien_response", "")

	var qa: Dictionary = await APIClient.run_qa(
		Global.qa_session_id, alien_line, player_text
	)

	var is_valid: bool  = qa.get("validity", false)
	var reason:  String = qa.get("reason",  "That response wasn't quite right.")
	var summary: String = qa.get("summary", player_text)

	if not is_valid:
		Dialogic.VAR.set("turn_valid", false)
		Dialogic.VAR.set("qa_reason",  reason)
		emit_signal("turn_resolved")
		return

	_turn += 1
	Dialogic.VAR.set("turn_valid",  true)
	Dialogic.VAR.set("turn_number", _turn)
	Dialogic.VAR.set("qa_reason",   "")

	PointCalculator.calculate_points(summary, _alien_idx)

	if _turn >= MAX_TURNS:
		Global.Aliens[_alien_idx]["visited"] = true
		Global.button_flags[_alien_idx]      = true
		Dialogic.VAR.set("game_over", true)
		emit_signal("turn_resolved")
		return

	var reply: String = await APIClient.run_alien(
		Global.alien_session_id, alien_line, summary
	)
	if reply == "":
		reply = "Hmm… interesting."

	Global.Aliens[_alien_idx]["alien_response"] = reply
	Dialogic.VAR.set("alien_response", reply)
	emit_signal("turn_resolved")
