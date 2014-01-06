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
	chat_log.innerHTML+="<p>"+myData["sender"]+": "+myData["message"]+"</p>";
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
	
function sendChatMessage(){
	var chat_to_send= document.getElementById("chat_to_send");
	var message={};
	message["proto_type"]="chat_message";
	message["message"]= chat_to_send.value;
	send_msg_server(message);
	chat_to_send.value='';
}

function handleKeyPress(e){
	if(e.keyCode === 13){
		sendChatMessage();
		return false;
	}
}
function send_msg_server(msg){
	ws.send(JSON.stringify(msg));
}

window.onload= connect_ws_server;
