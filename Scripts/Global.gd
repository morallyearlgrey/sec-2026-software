extends Node

const BASE_URL = "http://localhost:8000"
const PLAYER_ID = "mcdiggity"
var sessions = {}

# index, int
# name, string
# mood, string
# mbti, string
# situation, string arr
# dialogue_intro, string
# liked_words, string-int dict
# banned_words, string-int dict
# happiness_meter, float
# src, string
# points, int
const Aliens = {
}

var cur_alien_idx = 0;

func send_to_qa(input: String, alien_id: String):
	if not sessions.has("qa_agent"):
		push_error("no qa session ):")
		return
		
	var http = HTTPRequest.new();
	add_child(http);
	http.request_completed.connect(_on_qa_response.bind(http, input, alien_id));

	var url = "%s/apps/qa_agent/users/%s/sessions/%s/run" % [
		BASE_URL, PLAYER_ID, sessions["qa_agent"]
	];
	
	var body = JSON.stringify({
		"new_message": {
			"role": "user",
			"parts": [{ "text": input }]
		}
	}) # who is sending and the text the player wrote, we can replace role with alien or player

	http.request(url, ["Content-Type: application/json"], HTTPClient.METHOD_POST, body)

func _on_qa_response(result, response_code, headers, body, http: HTTPRequest, prompt: String, alien_id: String):
	http.queue_free()

	if response_code != 200:
		emit_signal("request_failed", "qa_agent", "QA request failed: %d" % response_code)
		return

	var json = JSON.parse_string(body.get_string_from_utf8())
	if not json:
		return

	# extract text from ADK response
	var raw_text = ""
	for event in json:
		if event.has("content") and event["content"].has("parts"):
			for part in event["content"]["parts"]:
				if part.has("text"):
					raw_text = part["text"]

	# parse the dict the QA agent returns
	var qa_result = JSON.parse_string(raw_text)
	if not qa_result:
		push_error("Could not parse QA response: %s" % raw_text)
		return

	if qa_result["validity"] == false:
		# tell the scene to show the rejection reason
		emit_signal("qa_rejected", qa_result["reason"], qa_result["summary"])
	else:
		# passed QA — score it and send to alien agent
		DialogueScorer.calculate_points(prompt, alien_id)
		send_message("alien_agent", prompt)

func get_alien(alien_id: int) -> Dictionary:
	return Aliens.get(alien_id, {})

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
