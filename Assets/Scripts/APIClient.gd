extends Node

# basically
# 1) parses and json stringifies agent responses, ensuring they are json
# 2) creates sessions for adk agents
# 3) calls generate aliens
# 4) basic request function
# 5) runs adk agent
# 6) completed https request

const BASE_URL = "http://localhost:8000"
const PLAYER_ID = "mcdiggity"

var req: HTTPRequest

signal reqdone(result: int, code: int, headers: PackedStringArray, body: PackedByteArray);

func _ready() -> void:
	req = HTTPRequest.new()
	add_child(req)
	req.request_completed.connect(_on_request_completed)
	
func _on_request_completed(result, code, headers, body) -> void:
	emit_signal("reqdone", result, code, headers, body);

# response is [result, code, headers, body]
# check that json is there, stringify it
# check for success X
# *method is the spec method, internally it's stored as ints
func send_request(method: int, url: String, body_dict: Dictionary = {}) -> Dictionary:
	var headers = ["Content-Type: application/json"];
	var str = "";
	
	if(body_dict.size()>0):
		str = JSON.stringify(body_dict);
	
	var isOk = req.request(url, headers, method, str);
	
	if(isOk!=OK):
		return {"error": "request send failed ):"};
	
	else:
		var res = await reqdone;
		
		if(res[0] == HTTPRequest.RESULT_SUCCESS):
			var json = JSON.new();
			var parse_err = json.parse(res[3].get_string_from_utf8());
			
			if( parse_err != OK):
				return {"error": "json_parse_error"}
		 
			return json.get_data()
			
		else:
			return {"error": "request send failed ):"};
				
	
# alien stuff
func generate_alien() -> Dictionary:
	return await send_request(HTTPClient.METHOD_GET, BASE_URL+"/generate-alien");
	
# make a session for the agent, could be qa or alien
func create_session(agent_name: String) -> String:
	var url  = "%s/apps/%s/users/%s/sessions" % [BASE_URL, agent_name, PLAYER_ID]
	
	var data = await send_request(HTTPClient.METHOD_POST, url)
	if(data.has("error")):
		return ""
	
	return data.get("id", "")
	
func run_agent(agent_name: String, session_id: String, message: String) -> String:
	var url = BASE_URL + "/run";
	var body = {
		"app_name":    agent_name,
		"user_id":     PLAYER_ID,
		"session_id":  session_id,
		"new_message": {
			"role":  "user",
			"parts": [{"text": message}]
		}
	}
	
	var data = await send_request(HTTPClient.METHOD_POST, url, body);
	if data.has("error"):
		return ""
		
	if data is Array:
		for event in data:
			if event.get("content", {}).get("role") == "model":
				for part in event["content"].get("parts", []):
					if part.has("text"):
						return part["text"]
	return ""

	
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
