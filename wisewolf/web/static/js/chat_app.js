require([
	"dojo/dom",
	"dojo/on",
	"kb/chat",
	"dojo/domReady!"
	], function(dom, on, chat){
		var room_id= document.URL.split("/")[4].replace('#','');
		var chat_log= dom.byId("chat_log_"+room_id);
		var chat_to_send= dom.byId("chat_to_send_"+room_id);
		var send_button= dom.byId("send_button_"+room_id);
		URL_split= document.URL.split("/");
		chat_room_seq= URL_split[URL_split.indexOf("chatting")+1].replace('#','');//get element which next of 'chat'
		var main_chat= new chat(chat_room_seq, dom.byId("chat_log_"+chat_room_seq), dom.byId("chatters_"+chat_room_seq));
		if(window.location.protocol=="https:"){
			main_chat.connect_server("wss://"+window.location.host+"/ws/chat/"+chat_room_seq);
		}else{
			main_chat.connect_server("ws://"+window.location.host+"/ws/chat/"+chat_room_seq);
		}
		var sendChatMessage= function(){
			var message={};
			message["proto_type"]="chat_message";
			message["message"]= chat_to_send.value;
			main_chat.send_msg_server(message);
			chat_to_send.value='';
		};
		on(send_button, "click", sendChatMessage);
		on(chat_to_send, "keypress", function(event){
			if(event.keyCode== 13){
				sendChatMessage();
			}
		})
		on(chat_to_send, "keyup", function(event){
			if(event.keyCode== 13){
				chat_to_send.value='';
			}
		})
		on(chat_log, "scroll", function(event){
			main_chat.req_past_message()	
		})
		on(window,"resize", function(){
			main_chat.auto_h_resize();
		})
		for(var i=0; i<10; i++){
			main_chat.auto_h_resize();
		}
	}
)
