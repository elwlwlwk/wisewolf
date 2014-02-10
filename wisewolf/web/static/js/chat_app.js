require([
	"dojo/dom",
	"dojo/on",
	"dojox/socket",
	"dojo/domReady!"
	], function(dom, on){
		URL_split= document.URL.split("/");
		chat_room_seq= URL_split[URL_split.indexOf("chatting")+1];//get element which next of 'chat'
		ws= dojox.socket("ws://165.194.104.192:8000/ws/chat/"+chat_room_seq);
		dojo.connect(ws,"onmessage", messageHandler);
		dojo.connect(ws,"onopen", openHandler);
		sendChatMessage= function(){
			var chat_to_send= dom.byId("chat_to_send");
			var message={};
			message["proto_type"]="chat_message";
			message["message"]= chat_to_send.value;
			send_msg_server(message);
			dom.byId("chat_to_send").value='';
		};
		on(dom.byId("send_button"), "click", sendChatMessage);
		on(dom.byId("chat_to_send"), "keypress", function(event){
			if(event.keyCode== 13){
				sendChatMessage();
			}
		})
		on(dom.byId("chat_to_send"), "keyup", function(event){
			if(event.keyCode== 13){
				dom.byId("chat_to_send").value='';
			}
		})
	}
)

var ws;
function connect_ws_server(){
	URL_split= document.URL.split("/");
	chat_room_seq= URL_split[URL_split.indexOf("chatting")+1];//get element which next of 'chat'
	ws= new WebSocket("ws://165.194.104.192:8000/ws/chat/"+chat_room_seq);
	ws.onopen= openHandler;
	ws.onmessage= messageHandler;
}
function openHandler(e){
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
			if(Number(chat_log.childNodes[i].id.split("_")[1])> myData["chat_seq"]&& Number(chat_log.childNodes[i-1].id.split("_")[1])< myData["chat_seq"]){
				new_chat= document.createElement("div");
				new_chat.setAttribute("id", "chat_"+myData["chat_seq"]);
				new_chat.innerHTML="<span>"+myData["sender"]+"</span>"+": "+"<span>"+myData["message"]+"</span>";
				chat_log.insertBefore(new_chat, chat_log.childNodes[i]);//TODO Not Tested!!
				break;
			}
		}
	}
	chat_log.scrollTop= chat_log.scrollHeight;
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
	
function send_msg_server(msg){
	ws.send(JSON.stringify(msg));
}


