define([
	"dojo/dom",
	"dojo/_base/window",
	"dojo/on",
	"dojox/socket"
], function(dom, window, on){

	var ws;
	var last_chat;

	function send_msg_server(message){
		ws.send(JSON.stringify(message));
	}
	function openHandler(e){
		message={"proto_type":"first_handshake", "user_id":dom.byId("user_id").value};
		send_msg_server(message);
	}
	function messageHandler(e){
		var myData= JSON.parse(e.data);
		switch (myData["proto_type"]){
			case "chat_message":
				chatMessageHandler(myData);
				break;
			case "room_stat":
				roomStatHandler(myData);
				break;
			case "heartbeat":
				heartbeatHandler(myData);
				break;
		}
	}
	function chatMessageHandler(myData){
		var chat_log= document.getElementById("chat_log");
		if(chat_log.childElementCount== 0){
			chat_log.innerHTML+="<div id=\"chat_"+myData["chat_seq"]+"\">"+"<span>"+myData["sender"]+"</span>"+": "+"<span>"+myData["message"]+"</span>"+"</div>";
		}
		else if(Number(chat_log.childNodes[chat_log.childElementCount].id.split("_")[1])< myData["chat_seq"]){
			chat_log.innerHTML+="<div id=\"chat_"+myData["chat_seq"]+"\">"+"<span>"+myData["sender"]+"</span>"+": "+"<span>"+myData["message"]+"</span>"+"</div>";
		}
		else{
			for(var i= chat_log.childElementCount; i>=1; i--){
				if(i== 1){
					new_chat= document.createElement("div");
					new_chat.setAttribute("id", "chat_"+myData["chat_seq"]);
					new_chat.innerHTML="<span>"+myData["sender"]+"</span>"+": "+"<span>"+myData["message"]+"</span>";
					chat_log.insertBefore(new_chat, chat_log.childNodes[i]);
					break;
				}
				if(Number(chat_log.childNodes[i].id.split("_")[1])>= myData["chat_seq"]&& Number(chat_log.childNodes[i-1].id.split("_")[1])<= myData["chat_seq"]){
					new_chat= document.createElement("div");
					new_chat.setAttribute("id", "chat_"+myData["chat_seq"]);
					new_chat.innerHTML="<span>"+myData["sender"]+"</span>"+": "+"<span>"+myData["message"]+"</span>";
					chat_log.insertBefore(new_chat, chat_log.childNodes[i]);//TODO Not Tested!!
					break;
				}
			}
		}
		if(myData["past_chat"]=="true"){
			last_chat.scrollIntoView(true);
		}
		else{
			chat_log.scrollTop= chat_log.scrollHeight;
		}
	}
	
	function roomStatHandler(myData){
		var chatters= myData["chatters"];
		var chatters_list= document.getElementById("chatters");
		chatters_list.innerHTML='';
		for(var i=0; i< chatters.length; i++){
			chatters_list.innerHTML+="<p>"+chatters[i]+"</p>";
		}
	}
	
	function heartbeatHandler(myData){
		var message={};
		message["proto_type"]= "heartbeat";
		message["heartbeat_key"]=myData["heartbeat_key"];
		send_msg_server(message);
	}
	
	function auto_h_resize(){
		var body= dom.byId("body")
		if(body.clientWidth){}
		dom.byId("body_content").style.height=body.clientHeight-58+"px";
		dom.byId("chat_wrapper").style.height=body.clientHeight-198+"px";
		dom.byId("chat_log").style.height=body.clientHeight-290+"px";
		dom.byId("chatters").style.height=body.clientHeight-290+"px";
		dom.byId("chat_log").scrollTop= chat_log.scrollHeight;
	}

	function req_past_message(){
		if(dom.byId("chat_log").scrollTop==0){
			message={};
			message["proto_type"]="req_past_messages";
			message["last_index"]=Number(dom.byId("chat_log").childNodes[1].id.split("_")[1]);
			if(message["last_index"]>1){
				last_chat=dom.byId("chat_log").childNodes[1];
				send_msg_server(message);
			}
		}
	}

	return{
		connect_server: function(host){
			ws= dojox.socket(host);
			dojo.connect(ws,"onmessage", messageHandler);
			dojo.connect(ws,"onopen", openHandler);
		},
		send_msg_server: function(msg){
			send_msg_server(msg);
		},
		scroll_lock: function(chat){
			last_chat= chat;
		},
		auto_height_resize: function(){
			auto_h_resize();
		},
		req_past_message: function(){
			req_past_message()
		}
	};
});
