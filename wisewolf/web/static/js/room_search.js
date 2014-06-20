require([
	"dojo/dom",
	"dojo/on",
	"dojo/_base/xhr",
	"kb/popup",
	"dojo/domReady!"
	], function(dom, on, xhr, popup){
	
		var input_room_search= dom.byId("input_room_search");
		var xhr_send_room_search= function(seq){
			dom.byId("room_load_progress").style.visibility="visible";
			seq= typeof seq !== 'object' ? seq : 0; //Because seq must be number type. When this function call as button event's call-back func, first args comes object of event.
			if(seq== 0){
				dom.byId("tbody_room_list").innerHTML="";
			}
			var xhrArgs={
				url: "/get_room_list",
				postData: JSON.stringify({"keyword":input_room_search.value, "seq":seq}),
				handleAs: "json",
				load: function(data){
					var room_list= data["room_info"];
					for(var seq in room_list){
						var tbody_room_list= dom.byId("tbody_room_list");
						
						var tr_room= document.createElement("tr");

						var td_mark= document.createElement("td");
						td_mark.classList.add("clickable");
						td_mark.classList.add("text-center");
						var span_mark= document.createElement("span");
						span_mark.classList.add("glyphicon");
						span_mark.classList.add("glyphicon-star-empty");
						span_mark.classList.add("td_room_mark");
						td_mark.appendChild(span_mark);
						tr_room.appendChild(td_mark);

						var td_title= document.createElement("td");
						td_title.innerHTML=room_list[seq]["title"];
						td_title.classList.add("clickable");
						td_title.classList.add("td_room_title");
						tr_room.appendChild(td_title);

						var td_participants= document.createElement("td");
						td_participants.innerHTML=room_list[seq]["cur_participants"]+ ' / '+ room_list[seq]["max_participants"];
						td_participants.classList.add("clickable");
						td_participants.classList.add("td_room_participants");
						td_participants.classList.add("text-center");
						tr_room.appendChild(td_participants);
						
						tbody_room_list.appendChild(tr_room);

					}
					dom.byId("room_load_progress").style.visibility="hidden";
				}
			}
			xhr.post(xhrArgs);
		};
		
		on(dom.byId("button_room_search"), "click", xhr_send_room_search);
		on(input_room_search, "keypress", function(event){
			if(event.keyCode== 13){
				xhr_send_room_search(0);
			}
		})
	}
)
