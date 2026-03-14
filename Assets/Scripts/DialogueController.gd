extends Node

#var cur_alien = {};
#
## create session, get the fucking damn alien 
#func setup_alien() -> void:
	#Global.num_turn=0;
	#cur_alien = Global.get_alien(Global.cur_alien_idx);
	#cur_alien["src"] = "res://Assets/Characters/images/alien%d.png" % (randi() % 8 + 1);
	#
	#Global.alien_session_id = await APIClient.create_session("alien_agent");
	#Global.qa_session_id = await APIClient.create_session("qa_agent");
	#
	#Dialogic.set_variable("alien_name", cur_alien["src"]);
	#Dialogic.set_variable("alien_image", cur_alien["name"]);
	#Global.set_variable("dynamic_line", cur_alien["dialogue_intro"]);
#
## should repeat Global.Aliens[cur_alien_idx]["num_turns"] amount
## might not be called # num_turns lol
#func take_turn() -> void:
	## get player input
	#var player_text = Dialogic.VAR.get("player_input")
	#
	## add timer logic here
	#
	## qa check
	#var qa_msg = "{\"question\": \"%s\"}\n{\"answer\": \"%s\"}" % [Dialogic.VAR.get("alien_response"), player_text];
	#var qa_reply  = await APIClient.run_agent("qa_agent", Global.qa_session_id, qa_msg);
	#var qa_parsed = APIClient.parse_agent_json(qa_reply);
	#
	#if(qa_parsed["validity"].value==true):
		#Global.num_turn+=1;
		## update the points ya
		#PointCalculator.calculate_points(qa_parsed, Global.cur_alien_idx);
		#
		#var to_alien_msg = {"id": "", "alien": "", "message": ""};
		#
		#var alien_msg = "{\"alien_dialog\": \"%s\"}\n{\"turn_summary\": \"%s\"}" % [Dialogic.VAR.get("alien_response"), to_alien_msg];
		#var alien_reply  = await APIClient.run_agent("alien_agent", Global.alien_session_id, alien_msg);
		#var alien_parsed = APIClient.parse_agent_json(alien_reply);
	#
	#else:
		#Global.set_variable("dynamic_line", qa_parsed["reason"]);
		#take_turn();
#
	#
# sorry peyton lol
func dynamic_dialogue() -> void:
	var lines = [
		"Fresh moonberries!",
		"Careful, those glow.",
		"Straight from the asteroid farms."
	]
	Global.dynamic_line = lines[0]
	
func static_dialogue():
	Global.set_variable("dynamic_line", "Fresh alien fruit!")
