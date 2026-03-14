extends Node

# APIClient handles all HTTP communication with the FastAPI server.
# Endpoints used:
#   GET  /generate-alien                              → alien data dict (includes "prompt")
#   POST /apps/{agent}/users/{uid}/sessions           → create session, returns {id}
#   POST /run-qa                                      → {validity, reason, summary}
#   POST /run-alien                                   → {reply}

const BASE_URL  = "http://localhost:8000"
const PLAYER_ID = "mcdiggity"

var _req: HTTPRequest

signal _req_done(result: int, code: int, headers: PackedStringArray, body: PackedByteArray)

func _ready() -> void:
	_req = HTTPRequest.new()
	add_child(_req)
	_req.request_completed.connect(_on_request_completed)

func _on_request_completed(result, code, headers, body) -> void:
	emit_signal("_req_done", result, code, headers, body)

# ── low-level ──────────────────────────────────────────────────────────────────

func _send(method: int, url: String, body_dict: Dictionary = {}) -> Dictionary:
	var headers  = ["Content-Type: application/json"]
	var body_str = ""
	if body_dict.size() > 0:
		body_str = JSON.stringify(body_dict)

	var ok = _req.request(url, headers, method, body_str)
	if ok != OK:
		push_error("APIClient: request failed to send → " + url)
		return {"error": "send_failed"}

	var res = await _req_done

	if res[0] != HTTPRequest.RESULT_SUCCESS:
		push_error("APIClient: HTTP error %d → %s" % [res[1], url])
		return {"error": "http_error_%d" % res[1]}

	var json = JSON.new()
	if json.parse(res[3].get_string_from_utf8()) != OK:
		push_error("APIClient: JSON parse error from " + url)
		return {"error": "json_parse"}

	return json.get_data()

# ── public API ─────────────────────────────────────────────────────────────────

## GET /generate-alien  →  full alien data dict (includes "prompt" key)
func generate_alien() -> Dictionary:
	return await _send(HTTPClient.METHOD_GET, BASE_URL + "/generate-alien")

## POST /apps/{agent}/users/{uid}/sessions  →  session id string
func create_session(agent_name: String) -> String:
	var url  = "%s/apps/%s/users/%s/sessions" % [BASE_URL, agent_name, PLAYER_ID]
	var data = await _send(HTTPClient.METHOD_POST, url)
	if data.has("error"):
		push_error("APIClient: create_session failed for " + agent_name)
		return ""
	return data.get("id", "")

## POST /run-qa  →  {validity: bool, reason: str, summary: str}
func run_qa(session_id: String, question: String, answer: String) -> Dictionary:
	var body = {
		"session_id": session_id,
		"question":   question,
		"answer":     answer,
	}
	var data = await _send(HTTPClient.METHOD_POST, BASE_URL + "/run-qa", body)
	if data.has("error"):
		return {"validity": false, "reason": "network error", "summary": ""}
	return data

## POST /run-alien  →  {reply: str}
## alien_prompt must be passed so each alien has its own unique personality.
func run_alien(session_id: String, alien_dialog: String, turn_summary: String, alien_prompt: String) -> String:
	var body = {
		"session_id":   session_id,
		"alien_dialog": alien_dialog,
		"turn_summary": turn_summary,
		"alien_prompt": alien_prompt,
	}
	var data = await _send(HTTPClient.METHOD_POST, BASE_URL + "/run-alien", body)
	if data.has("error"):
		return ""
	return data.get("reply", "")

## Strips markdown fences and parses JSON from an agent reply string.
func parse_agent_json(reply: String) -> Dictionary:
	var cleaned = reply.strip_edges()
	cleaned = cleaned.trim_prefix("```json").trim_prefix("```").trim_suffix("```").strip_edges()
	var json = JSON.new()
	if json.parse(cleaned) != OK:
		return {}
	var data = json.get_data()
	if data is Dictionary:
		return data
	return {}
