extends Node

const BASE_URL = "http://localhost:8000"
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
	# If the node is busy, force-cancel it so we can send the new one immediately
	if _req.get_http_client_status() != HTTPClient.STATUS_DISCONNECTED:
		_req.cancel_request()

	var headers = ["Content-Type: application/json"]
	var body_str = JSON.stringify(body_dict) if body_dict.size() > 0 else ""

	var ok = _req.request(url, headers, method, body_str)
	if ok != OK:
		return {"error": "send_failed"}

	var res = await _req_done
	
	# Always parse the body to see what happened
	var data = JSON.parse_string(res[3].get_string_from_utf8())
	return data if data != null else {"error": "json_parse"}

# ── public API ─────────────────────────────────────────────────────────────────

func get_alien(index: int) -> Dictionary:
	# DialogueController calls this. It will now wait patiently if busy.
	return await _send(HTTPClient.METHOD_GET, BASE_URL + "/alien/chat?index=" + str(index))

func chat_with_alien(alien_id: String, message: String, points: int) -> Dictionary:
	var body = {
		"player_id": PLAYER_ID,
		"alien_id": alien_id,
		"message": message,
		"current_points": points
	}
	return await _send(HTTPClient.METHOD_POST, BASE_URL + "/alien/chat", body)
