var back_ground;
define([
	"dojo/dom",
	"dojo/on"
], function(dom, on){
	function popup(element){
		var body= dom.byId("body");
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
	function popup_positioning(element){
		var body= dom.byId("body");
		element.style.top= (body.clientHeight-element.clientHeight)/2+"px";
		element.style.left= (body.clientWidth-element.clientWidth)/2+"px";
	}
	return{
		popup: function(element){
			popup(element);
		},
		alert_popup: function(str_alert){
			alert_window= document.createElement("div");
			alert_window.setAttribute("class", "popup_window");
			alert_window.innerText=str_alert;
			popup(alert_window);
		}
	}
})
