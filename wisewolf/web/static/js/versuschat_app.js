require([
	"dojo/dom",
	"dojo/on",
	"dojo/topic",
	"kb/chat",
	"kb/popup",
	"dojo/domReady!"
	], function(dom, on, topic, chat, popup){
		var pros_cons= dom.byId("input_pros_cons")
		if(pros_cons.value== ''){
			popup.pros_cons();
		}
		var room_id= document.URL.split("/")[4].replace('#','');
		var chat_log= dom.byId("chat_log_"+room_id);
		var chat_to_send= dom.byId("chat_to_send_"+room_id);
		var send_button= dom.byId("send_button_"+room_id);
		URL_split= document.URL.split("/");
		chat_room_seq= URL_split[URL_split.indexOf("chatting")+1].replace('#','');//get element which next of 'chat'
		var main_chat= new chat(chat_room_seq, dom.byId("chat_log_"+chat_room_seq), dom.byId("chatters_"+chat_room_seq));
		main_chat.connect_server("ws://clug2.clug.kr/ws/chat/"+chat_room_seq);
		sendChatMessage= function(){
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

		var chat_to_send_support= dom.byId("chat_to_send_"+room_id+"_support");
		var send_button_support= dom.byId("send_button_"+room_id+"_support");
		var chat_log_support= dom.byId("chat_log_"+room_id+"_support");
		var support_chat= new chat(chat_room_seq+"_support", dom.byId("chat_log_"+chat_room_seq+"_support"),
			dom.byId("chatters_"+chat_room_seq+"_support"));

		if(pros_cons.value!=""){//this is for room opener or pre-selected user
			if(pros_cons.value="pros"){
				support_chat.connect_server("ws://clug2.clug.kr/ws/chat/"+chat_room_seq+"_supportA");
			}else{
				support_chat.connect_server("ws://clug2.clug.kr/ws/chat/"+chat_room_seq+"_supportB");
			}
		}else{
			topic.subscribe("select_pros_cons", function(text){
				if(text== "pros"){
					support_chat.connect_server("ws://clug2.clug.kr/ws/chat/"+chat_room_seq+"_supportA");
				}else{
					support_chat.connect_server("ws://clug2.clug.kr/ws/chat/"+chat_room_seq+"_supportB");
				}
			})
		}
		sendChatMessage_support= function(){
			var message={};
			message["proto_type"]="chat_message";
			message["message"]= chat_to_send_support.value;
			support_chat.send_msg_server(message);
			chat_to_send_support.value='';
		};
		on(send_button_support, "click", sendChatMessage_support);
		on(chat_to_send_support, "keypress", function(event){
			if(event.keyCode== 13){
				sendChatMessage_support();
			}
		})
		on(chat_to_send_support, "keyup", function(event){
			if(event.keyCode== 13){
				chat_to_send_support.value='';
			}
		})
		on(window,"resize", function(){
			support_chat.auto_h_resize();
		})
		on(chat_log_support, "scroll", function(event){
			support_chat.req_past_message()	
		})
		
		for(var i=0; i<10; i++){
			main_chat.auto_h_resize();
			support_chat.auto_h_resize();
		}
	}
)
