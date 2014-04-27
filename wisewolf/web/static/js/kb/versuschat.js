define(["dojo/_base/declare"], function(declare){
		function my(){
			alert(this.a);
		}
		return declare(null, {
			constructor: function(a){
				this.a= a;
				this.test();
			},
			test:my
		})
	}
)
