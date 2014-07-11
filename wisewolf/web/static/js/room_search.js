require([
	"dojo/dom",
	"dojo/dom-construct",
	"dojo/dom-class",
	"dojo/on",
	"dojo/_base/xhr",
	"dojo/query",
	"kb/popup",
	"dojo/domReady!"
	], function(dom, domConstruct, domClass, on, xhr, query, popup){
	
		function display_tags(tags){
			var td_info_tags= dom.byId("div_info_tags");
			td_info_tags.innerHTML='';
			sorted_tags=[]
			for(var key in tags){
				sorted_tags.push([tags[key]['up'], tags[key]['tag'], tags[key]['down']]);
			}
			sorted_tags.sort(function(m, n){return m[0]-n[0]});
			for(var i= sorted_tags.length-1; i>=0; i--){
				var tag= document.createElement("span");
				var text= document.createTextNode(", ");
				tag.setAttribute("id", "tag_button_"+sorted_tags[i][1]);
				tag.setAttribute("class", "btn-outline");
				tag.setAttribute("name", "tag");
				tag.setAttribute("style", "word-break: break-all;");
				tag.innerHTML= sorted_tags[i][1];
				td_info_tags.appendChild(tag);
				td_info_tags.appendChild(text);
			}
		}
		var input_room_search= dom.byId("input_room_search");
		var xhr_get_room_info= function(room_seq){
			dom.byId("div_room_info").style.display="none";
			dom.byId("room_info_progress").style.display="block";
			var xhrArgs={
				url: "/get_room_info",
				postData: JSON.stringify({"room_seq": room_seq}),
				handleAs: "json",
				load: function(data){
					dom.byId("td_info_title").innerHTML=data["room_title"];
					dom.byId("td_info_kind").innerHTML=data["room_kind"];
					display_tags(data['tags']);

					dom.byId("td_info_kind");
					dom.byId("a_enter_room").href= "/chatting/"+data["room_seq"];
					dom.byId("a_enter_room").style.display= "";
					dom.byId("room_info_progress").style.display="none";
					dom.byId("div_room_info").style.display="block";
					return;
				}
			}
			xhr.post(xhrArgs);
		}
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
						
						var tr_room= domConstruct.create("tr");
						domClass.add(tr_room, ["tr_room"])

						var td_mark= domConstruct.create("td");
						domClass.add(td_mark, ["clickable", "text-center"]);
						var span_mark= domConstruct.create("span");
						domClass.add(span_mark, ["glyphicon", "glyphicon-star-empty", "td_room_mark"]);
						td_mark.appendChild(span_mark);
						tr_room.appendChild(td_mark);

						var td_title= domConstruct.create("td");
						td_title.innerHTML=room_list[seq]["title"];
						domClass.add(td_title, ["clickable", "td_room_title"]);
						td_title.id=("td_title_"+room_list[seq]["key"]);
						tr_room.appendChild(td_title);
						on(tr_room, "click", function(e){
							var room_seq= e.target.id.split("_")[2];
							xhr_get_room_info(room_seq);
						});

						var td_participants= domConstruct.create("td");
						td_participants.innerHTML=room_list[seq]["cur_participants"]+ ' / '+ room_list[seq]["max_participants"];
						domClass.add(td_participants, ["clickable", "td_room_participants", "text-center"]);
						td_participants.id='td_participants_'+room_list[seq]["key"];
						tr_room.appendChild(td_participants);
						
						tbody_room_list.appendChild(tr_room);

					}
					dom.byId("room_load_progress").style.visibility="hidden";
				}
			}
			xhr.post(xhrArgs);
		};
		
		on(dom.byId("button_room_search"), "click", xhr_send_room_search);
		on(dom.byId("td_get_more_room"),"click", function(){
			xhr_send_room_search(query(".tr_room").length+1);
		});
		on(input_room_search, "keypress", function(event){
			if(event.keyCode== 13){
				xhr_send_room_search(0);
			}
		})
		xhr_send_room_search(0);
	}
)
