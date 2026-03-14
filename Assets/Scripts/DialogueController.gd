extends Node

# ── constants ──────────────────────────────────────────────────────────────────
const MAX_TURNS     = 5
const INPUT_TIMEOUT = 30.0   # seconds before auto-submit

# ── state ──────────────────────────────────────────────────────────────────────
var _alien_idx:  int    = -1
var _turn:       int    = 0
var _timer:      Timer  = null
var _timed_out:  bool   = false

# Dialogic signal handles (stored so we can disconnect later)
var _timeline_end_handle = null

# ── called by ButtonController when a map pin is clicked ──────────────────────

func start_alien_encounter(alien_idx: int) -> void:
	_alien_idx = alien_idx
	_turn      = 0

	# 1. Generate the alien data from the server
	var alien_data: Dictionary = await APIClient.generate_alien()
	if alien_data.has("error") or alien_data.is_empty():
		push_error("DialogueController: generate_alien failed")
		return

	# 2. Create ADK sessions for both agents
	Global.alien_session_id = await APIClient.create_session("alien_agent")
	Global.qa_session_id    = await APIClient.create_session("qa_agent")

	# 3. Store alien in Global and push Dialogic vars
	Global.register_alien(alien_idx, alien_data)
	Global.cur_alien_idx = alien_idx

	# 4. Build the alien's opening line by sending the greeting to the agent
	#    so the session has context.  We pass an empty turn_summary for turn 0.
	var intro_reply: String = await APIClient.run_alien(
		Global.alien_session_id,
		alien_data.get("greeting", "Hello."),
		"(conversation start)"
	)
	if intro_reply == "":
		intro_reply = alien_data.get("greeting", "Hello.")

	Global.Aliens[alien_idx]["alien_response"] = intro_reply
	Dialogic.VAR.set("alien_response", intro_reply)
	Dialogic.VAR.set("alien_name",     alien_data.get("name", "???"))
	Dialogic.VAR.set("alien_image",    Global.Aliens[alien_idx]["src"])
	Dialogic.VAR.set("player_input",   "")
	Dialogic.VAR.set("turn_valid",     false)
	Dialogic.VAR.set("qa_reason",      "")
	Dialogic.VAR.set("turn_number",    0)
	Dialogic.VAR.set("game_over",      false)

	# 5. Kick off the single shared timeline
	Dialogic.start("alien_encounter")


# ── called from the timeline via `do DialogueController.submit_player_input()` ─

## The timeline calls this after the player fills in the TextInput node.
## The Dialogic TextInput layer writes to Dialogic.VAR["player_input"].
func submit_player_input() -> void:
	# Stop any running timer immediately
	if _timer != null and not _timer.is_stopped():
		_timer.stop()

	var player_text: String = Dialogic.VAR.get("player_input")
	await _process_turn(player_text)


# ── timer ──────────────────────────────────────────────────────────────────────

func _start_input_timer() -> void:
	if _timer == null:
		_timer = Timer.new()
		_timer.one_shot = true
		add_child(_timer)
		_timer.timeout.connect(_on_input_timeout)

	_timed_out = false
	_timer.start(INPUT_TIMEOUT)


func _on_input_timeout() -> void:
	_timed_out = true
	# Auto-submit whatever the player has typed so far
	var player_text: String = Dialogic.VAR.get("player_input")
	# Signal the timeline to stop waiting and proceed
	Dialogic.VAR.set("timed_out", true)
	await _process_turn(player_text)


# ── core turn pipeline ─────────────────────────────────────────────────────────

func _process_turn(player_text: String) -> void:
	var alien_line: String = Global.Aliens[_alien_idx].get("alien_response", "")

	# ── QA check ────────────────────────────────────────────────────────────
	var qa_result: Dictionary = await APIClient.run_qa(
		Global.qa_session_id,
		alien_line,
		player_text
	)

	var is_valid: bool   = qa_result.get("validity", false)
	var reason:   String = qa_result.get("reason",   "Invalid response.")
	var summary:  String = qa_result.get("summary",  player_text)

	if not is_valid:
		# Tell the timeline to re-prompt the player with the reason
		Dialogic.VAR.set("turn_valid", false)
		Dialogic.VAR.set("qa_reason",  reason)
		# Restart the timer for the re-prompt
		_start_input_timer()
		return

	# ── valid turn ───────────────────────────────────────────────────────────
	_turn += 1
	Dialogic.VAR.set("turn_number", _turn)
	Dialogic.VAR.set("turn_valid",  true)
	Dialogic.VAR.set("qa_reason",   "")

	# Point calculation
	PointCalculator.calculate_points(summary, _alien_idx)

	if _turn >= MAX_TURNS:
		# Conversation over
		Global.Aliens[_alien_idx]["visited"] = true
		Global.button_flags[_alien_idx]      = true
		Dialogic.VAR.set("game_over", true)
		# The timeline should branch to its end label when game_over == true
		return

	# ── alien replies ────────────────────────────────────────────────────────
	var alien_reply: String = await APIClient.run_alien(
		Global.alien_session_id,
		alien_line,
		summary
	)
	if alien_reply == "":
		alien_reply = "Hmm... interesting."

	Global.Aliens[_alien_idx]["alien_response"] = alien_reply
	Dialogic.VAR.set("alien_response", alien_reply)

	# Resume the timeline — it was paused at `do await DialogueController.submit_player_input()`
	# The timeline loop will now show alien_response and start_input_timer again.
	_start_input_timer()


# ── called from timeline: `do DialogueController.begin_player_input()` ────────

## Tells DialogueController to start the 30-second countdown.
## The timeline must NOT advance past this call automatically — it should
## pause using Dialogic's TextInput node which waits for the player.
func begin_player_input() -> void:
	Dialogic.VAR.set("timed_out", false)
	_start_input_timer()
