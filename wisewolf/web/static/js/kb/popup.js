define([
	"dojo/dom",
	"dojo/on",
	"dojo/_base/xhr"
], function(dom, on, xhr){
	function popup(element){
		var body= dom.byId("body");
		var back_ground= dom.byId("popup_background");
		if(back_ground!= null)
			close_popup();
		back_ground= document.createElement("div");
		back_ground.setAttribute("class","popup_background");
		back_ground.setAttribute("id", "popup_background");
		back_ground.appendChild(element);
		body.appendChild(back_ground);
		popup_positioning(element)
		on(window,"resize", function(){
			popup_positioning(element)
		})
	}

	function popup_xhr(path, callback, width){
		function display_popup(data){
			var popup_window= document.createElement("div");
			if(width== null){
				popup_window.setAttribute("class", "popup_window");
			}
			else if(width== "moderate"){
				popup_window.setAttribute("class", "popup_window moderate_width");
			}
			popup_window.innerHTML=data;
			popup(popup_window);

			if(callback!= null){
				callback();
			}
			popup_positioning(popup_window);
		}
		var xhrArgs={
			url: path,
			handleAs: "text",
			load: display_popup
		}
		xhr.get(xhrArgs);
	}

	function popup_positioning(element){
		var body= dom.byId("body");
		element.style.top= (body.clientHeight-element.clientHeight)/2+"px";
		element.style.left= (body.clientWidth-element.clientWidth)/2+"px";
	}
	function close_popup(){
		if(dom.byId("popup_background").remove== null){
			dom.byId("popup_background").outerHTML=''; //This is for IE11 support
		}
		else{
			dom.byId("popup_background").remove();
		}
	}
	return{
		popup: function(element){
			popup(element);
		},
		popup_xhr: function(path, callback){
			popup_xhr(path, callback);
		},
		alert_popup: function(str_alert){
			popup_xhr("/popup/alert.html", function(){
				on(dom.byId("btn_confirm"), "click", close_popup);
				dom.byId("alert_content").innerHTML= str_alert;
			});
		},
		new_room: function(){
			popup_xhr("/popup/newroom.html", function(){
				on(dom.byId("btn_cancel"), "click", close_popup);
			}, "moderate");
		},
		close_popup: function(){
			close_popup();
		}
	}
})
