require([
	"dojo/dom",
	"dojo/on",
	"dojo/_base/xhr",
	"dojo/domReady!"
	], function(dom, on, xhr){
	
		var input_room_search= dom.byId("input_room_search");
		var xhr_send_room_search= function(seq){
			seq= typeof seq !== 'object' ? seq : 0; //Because seq must be number type. When this function call as button event's call-back func, first args comes object of event.
			var xhrArgs={
				url: "/get_room_list",
				postData: JSON.stringify({"keyword":input_room_search.value, "seq":seq}),
				handleAs: "json",
				load: function(data){
					alert(data);
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
