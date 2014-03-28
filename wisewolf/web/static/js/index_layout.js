require([
	"dojo/dom",
	"dojo/on",
	"kb/popup",
	"dojo/domReady!"
	], function(dom, on, popup){
		on(dom.byId("a_newchat"), "click", function(){
			popup.new_room();
		})

	}
)
