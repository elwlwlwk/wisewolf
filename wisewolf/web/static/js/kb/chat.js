define([
	"dojo/dom",
	"dojo/_base/window",
	"dojo/on",
	"dojox/socket",
	"dojo/_base/declare"
], function(dom, window, on, socket, declare){
	return declare(null, {
		constructor:function(room_id, chat_log, chatters_list){
			this.room_id= room_id;
			this.chat_log= chat_log;
			this.chatters_list= chatters_list;
			this.div_vote=dom.byId("div_vote");
			this.list_chatters=[];
		},
		connect_server:function(host){
			this.ws= dojox.socket(host);
			this.ws.chat= this;
			dojo.connect(this.ws,"onmessage", this.messageHandler);
			dojo.connect(this.ws,"onopen", this.openHandler);
		},
		messageHandler:function(e){
			var myData= JSON.parse(e.data);
			switch (myData["proto_type"]){
				case "chat_message":
					this.chat.chatMessageHandler(myData);
					break;
				case "room_stat":
					this.chat.roomStatHandler(myData);
					break;
				case "heartbeat":
					this.chat.heartbeatHandler(myData);
					break;
			}
		},
		openHandler:function(e){
			message={"proto_type":"first_handshake", "user_id":dom.byId("user_id").value};
			this.chat.send_msg_server(message);
		},
		send_msg_server:function(message){
			this.ws.send(JSON.stringify(message));
		},
		get_list_chatters:function(){
			return this.list_chatters;	
		},
		chatMessageHandler:chatMessageHandler,
		roomStatHandler:roomStatHandler,
		heartbeatHandler:heartbeatHandler,
		req_past_message:req_past_message,
		auto_h_resize:auto_h_resize
	})
	
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
		if(this.chat_log.childElementCount== 0){
			this.chat_log.innerHTML+="<div id=\"chat_"+myData["chat_seq"]+"\">"+"<span>"+myData["sender"]+"</span>"+": "+"<span>"+myData["message"]+"</span>"+"</div>";
		}
		else if(Number(this.chat_log.childNodes[this.chat_log.childElementCount].id.split("_")[1])< myData["chat_seq"]){
			this.chat_log.innerHTML+="<div id=\"chat_"+myData["chat_seq"]+"\">"+"<span>"+myData["sender"]+"</span>"+": "+"<span>"+myData["message"]+"</span>"+"</div>";
		}
		else{
			for(var i= this.chat_log.childElementCount; i>=1; i--){
				if(i== 1){
					new_chat= document.createElement("div");
					new_chat.setAttribute("id", "chat_"+myData["chat_seq"]);
					new_chat.innerHTML="<span>"+myData["sender"]+"</span>"+": "+"<span>"+myData["message"]+"</span>";
					this.chat_log.insertBefore(new_chat, this.chat_log.childNodes[i]);
					break;
				}
				if(Number(this.chat_log.childNodes[i].id.split("_")[1])>= myData["chat_seq"]&& Number(this.chat_log.childNodes[i-1].id.split("_")[1])<= myData["chat_seq"]){
					new_chat= document.createElement("div");
					new_chat.setAttribute("id", "chat_"+myData["chat_seq"]);
					new_chat.innerHTML="<span>"+myData["sender"]+"</span>"+": "+"<span>"+myData["message"]+"</span>";
					this.chat_log.insertBefore(new_chat, this.chat_log.childNodes[i]);//TODO Not Tested!!
					break;
				}
			}
		}
		if(myData["past_chat"]=="true"){
			last_chat.scrollIntoView(true);
		}
		else{
			this.chat_log.scrollTop= this.chat_log.scrollHeight;
		}
	}
	
	function roomStatHandler(myData){
		var chatters= myData["chatters"];
		this.chatters_list.innerHTML='';
		for(var i=0; i< chatters.length; i++){
			this.chatters_list.innerHTML+="<p>"+chatters[i]+"</p>";
			this.list_chatters.push(chatters[i]);
		}
	}
	
	function heartbeatHandler(myData){
		var message={};
		message["proto_type"]= "heartbeat";
		message["heartbeat_key"]=myData["heartbeat_key"];
		this.send_msg_server(message);
	}
	
	function auto_h_resize(){
		var body= dom.byId("body")
		if(body.clientWidth){}
		dom.byId("body_content").style.height=body.clientHeight-58+"px";
		dom.byId("chat_wrapper").style.height=body.clientHeight-this.div_vote.clientHeight-70+"px";
		this.chat_log.style.height=body.clientHeight-this.div_vote.clientHeight-160+"px";
		this.chatters_list.style.height=body.clientHeight-this.div_vote.clientHeight-160+"px";
		this.chat_log.scrollTop= this.chat_log.scrollHeight;
	}

	function req_past_message(){
		if(this.chat_log.scrollTop==0){
			message={};
			message["proto_type"]="req_past_messages";
			message["last_index"]=Number(this.chat_log.childNodes[1].id.split("_")[1]);
			if(message["last_index"]>1){
				last_chat=this.chat_log.childNodes[1];
				this.send_msg_server(message);
			}
		}
	}
});
