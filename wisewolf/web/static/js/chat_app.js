require([
	"dojo/dom",
	"dojo/on",
	"kb/chat",
	"dojo/domReady!"
	], function(dom, on, chat){
		URL_split= document.URL.split("/");
		chat_room_seq= URL_split[URL_split.indexOf("chatting")+1];//get element which next of 'chat'
		chat.connect_server("ws://165.194.104.192:8000/ws/chat/"+chat_room_seq);
		chat.auto_height_resize();
		on(window,"resize", function(){
			chat.auto_height_resize();
		})
		sendChatMessage= function(){
			var chat_to_send= dom.byId("chat_to_send");
			var message={};
			message["proto_type"]="chat_message";
			message["message"]= chat_to_send.value;
			chat.send_msg_server(message);
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
		on(dom.byId("chat_log"), "scroll", function(event){
			chat.req_past_message()	
		})
	}
)
