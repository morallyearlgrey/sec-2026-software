extends Node

# ══════════════════════════════════════════════════════════════════════════════
# DialogueController — manages the full alien conversation pipeline.
#
# Turn flow (driven by alien_encounter.dtl):
#   1. Timeline shows alien_response text (with portrait via alien_image var)
#   2. Timeline calls: do DialogueController.show_input()
#   3. Timeline waits: signal DialogueController turn_resolved
#   4. Player types + submits (or 30 s timer fires)
#   5. _process_turn() async:
#        a. POST /run-qa  — validate player text
#        b. Invalid → set qa_reason, turn_valid=false, emit turn_resolved
#           → timeline shows qa_reason, jumps back to turn_start
#        c. Valid   → calculate points, turn_valid=true
#        d. Turn 5  → set game_over=true, emit turn_resolved → farewell
#        e. Else    → POST /run-alien → set alien_response, emit turn_resolved
#           → timeline shows new alien_response, jumps back to turn_start
# ══════════════════════════════════════════════════════════════════════════════

const MAX_TURNS     = 5
const INPUT_TIMEOUT = 30.0

var _alien_idx:    int    = -1
var _turn:         int    = 0
var _alien_prompt: String = ""
var _time_left:    float  = INPUT_TIMEOUT
var _processing:   bool   = false   # guard against double-submit

var _timer:           Timer    = null
var _overlay_canvas:  Node     = null
var _line_edit:       LineEdit = null
var _countdown_label: Label    = null
var _speaker_label:   Label    = null

signal turn_resolved


# ══════════════════════════════════════════════════════════════════════════════
# Entry point — ButtonController calls this
# ══════════════════════════════════════════════════════════════════════════════

func start_alien_encounter(alien_idx: int) -> void:
	_alien_idx    = alien_idx
	_turn         = 0
	_alien_prompt = ""
	_processing   = false

	# ── 1. Generate alien data ────────────────────────────────────────────────
	var alien_data: Dictionary = await APIClient.generate_alien()
	if alien_data.has("error") or alien_data.is_empty():
		push_error("DialogueController: generate_alien failed")
		return

	_alien_prompt = alien_data.get("prompt", "")

	# ── 2. Create fresh sessions for this encounter ───────────────────────────
	Global.alien_session_id = await APIClient.create_session("alien_agent")
	Global.qa_session_id    = await APIClient.create_session("qa_agent")

	# ── 3. Register alien in Global (sets alien_%d.png image path) ────────────
	Global.register_alien(alien_idx, alien_data)
	Global.cur_alien_idx = alien_idx

	# ── 4. Get the alien's opening line ───────────────────────────────────────
	var intro: String = await APIClient.run_alien(
		Global.alien_session_id,
		alien_data.get("greeting", "Hello."),
		"(conversation start)",
		_alien_prompt
	)
	if intro == "":
		intro = alien_data.get("greeting", "Hello.")

	Global.Aliens[alien_idx]["alien_response"] = intro

	# ── 5. Seed all Dialogic vars before starting the timeline ────────────────
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
# Called synchronously from timeline: do DialogueController.show_input()
# The timeline immediately hits "signal DialogueController turn_resolved" next,
# which blocks until we emit turn_resolved after async work completes.
# ══════════════════════════════════════════════════════════════════════════════

func show_input() -> void:
	_processing = false
	Dialogic.VAR.set("player_input", "")
	Dialogic.VAR.set("timed_out",    false)
	_build_overlay_if_needed()
	if _speaker_label:
		_speaker_label.text = str(Dialogic.VAR.get("alien_name")) + " is waiting…"
	_overlay_canvas.show()
	_line_edit.text = ""
	_line_edit.grab_focus()
	_start_countdown()


# ══════════════════════════════════════════════════════════════════════════════
# Timer — ticks every second, auto-submits at 0
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
		Dialogic.VAR.set("timed_out", true)
		_submit(_line_edit.text.strip_edges() if _line_edit else "")


func _update_countdown() -> void:
	if _countdown_label:
		_countdown_label.text = str(int(max(_time_left, 0)))


# ══════════════════════════════════════════════════════════════════════════════
# Overlay — built once, reused each turn
# CanvasLayer at layer 200 keeps it above Dialogic (which uses ~10–100)
# ══════════════════════════════════════════════════════════════════════════════

func _build_overlay_if_needed() -> void:
	if _overlay_canvas != null:
		return

	var canvas := CanvasLayer.new()
	canvas.layer = 200
	canvas.name  = "InputOverlay"
	get_tree().root.add_child(canvas)
	_overlay_canvas = canvas

	# Full-width strip pinned to the bottom of the screen
	var root_ctrl := Control.new()
	root_ctrl.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	root_ctrl.offset_top    = -210.0
	root_ctrl.offset_bottom = 0.0
	root_ctrl.offset_left   = 0.0
	root_ctrl.offset_right  = 0.0
	canvas.add_child(root_ctrl)

	# Dark semi-transparent background panel
	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.05, 0.05, 0.1, 0.88)
	root_ctrl.add_child(bg)

	# VBox for both rows
	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	vbox.offset_left   = 28.0
	vbox.offset_right  = -28.0
	vbox.offset_top    = 14.0
	vbox.offset_bottom = -14.0
	vbox.add_theme_constant_override("separation", 12)
	root_ctrl.add_child(vbox)

	# ── Row 1: speaker label + countdown box ──────────────────────────────────
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

	# Countdown: panel with a big bold number inside
	var cd_panel := PanelContainer.new()
	cd_panel.custom_minimum_size = Vector2(90, 90)
	top_row.add_child(cd_panel)

	var cd_lbl := Label.new()
	cd_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cd_lbl.vertical_alignment   = VERTICAL_ALIGNMENT_CENTER
	cd_lbl.add_theme_font_size_override("font_size", 48)
	cd_lbl.add_theme_color_override("font_color", Color(1.0, 0.3, 0.15))
	cd_lbl.text = "30"
	cd_panel.add_child(cd_lbl)
	_countdown_label = cd_lbl

	# ── Row 2: text input + submit button ─────────────────────────────────────
	var bot_row := HBoxContainer.new()
	bot_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bot_row.add_theme_constant_override("separation", 12)
	vbox.add_child(bot_row)

	var le := LineEdit.new()
	le.placeholder_text      = "Type your response here…"
	le.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	le.custom_minimum_size   = Vector2(0, 70)
	le.add_theme_font_size_override("font_size", 28)
	bot_row.add_child(le)
	_line_edit = le

	var btn := Button.new()
	btn.text                = "Submit"
	btn.custom_minimum_size = Vector2(170, 70)
	btn.add_theme_font_size_override("font_size", 28)
	bot_row.add_child(btn)

	btn.pressed.connect(_on_submit_pressed)
	le.text_submitted.connect(func(_t): _on_submit_pressed())


func _on_submit_pressed() -> void:
	if _processing:
		return
	_stop_countdown()
	_submit(_line_edit.text.strip_edges() if _line_edit else "")


func _submit(text: String) -> void:
	if _processing:
		return
	_processing = true
	_overlay_canvas.hide()
	# call_deferred so the timeline's signal-wait is active before we start
	# awaiting HTTP calls and eventually emit turn_resolved.
	_process_turn.call_deferred(text)


# ══════════════════════════════════════════════════════════════════════════════
# Core async pipeline — runs after every player submission
# ══════════════════════════════════════════════════════════════════════════════

func _process_turn(player_text: String) -> void:
	var alien_line: String = Global.Aliens[_alien_idx].get("alien_response", "")

	# ── 1. QA validation ───────────────────────────────────────────────────────
	var qa: Dictionary = await APIClient.run_qa(
		Global.qa_session_id, alien_line, player_text
	)

	# Robust validity extraction — handles bool or string "true"/"false"
	var raw_valid = qa.get("validity", false)
	var is_valid: bool = raw_valid == true or str(raw_valid).to_lower() == "true"

	var reason:  String = str(qa.get("reason",  "That response wasn't quite right."))
	var summary: String = str(qa.get("summary", player_text))

	if not is_valid:
		Dialogic.VAR.set("turn_valid", false)
		Dialogic.VAR.set("qa_reason",  reason)
		emit_signal("turn_resolved")
		return

	# ── 2. Valid turn ──────────────────────────────────────────────────────────
	_turn += 1
	Dialogic.VAR.set("turn_valid",  true)
	Dialogic.VAR.set("turn_number", _turn)
	Dialogic.VAR.set("qa_reason",   "")

	PointCalculator.calculate_points(summary, _alien_idx)

	# ── 3. End of conversation? ────────────────────────────────────────────────
	if _turn >= MAX_TURNS:
		Global.Aliens[_alien_idx]["visited"] = true
		Global.button_flags[_alien_idx]      = true
		Dialogic.VAR.set("game_over", true)
		emit_signal("turn_resolved")
		return

	# ── 4. Get alien's next line ───────────────────────────────────────────────
	var reply: String = await APIClient.run_alien(
		Global.alien_session_id, alien_line, summary, _alien_prompt
	)
	if reply == "":
		reply = "Hmm… interesting."

	Global.Aliens[_alien_idx]["alien_response"] = reply
	Dialogic.VAR.set("alien_response", reply)

	emit_signal("turn_resolved")
