/**
 * Waiting bar on top of the map. Is visible when the number of calls to
 * addLoading is bigger than of removeLoading
 */
var loader = {
	raiseEventBool: false,
	counter: 0,
	addLoading: function() {
		if(this.counter==0){
			$("#loader").fadeIn("slow");
		}
		this.counter = this.counter + 1;
	},
	removeLoading: function() {
		this.counter = this.counter - 1;
		if(this.counter==0){
			$("#loader").fadeOut("slow");
			if(this.raiseEventBool){
				var event = new CustomEvent("overlaysReady");
				document.dispatchEvent(event);
				this.raiseEventBool = false;
			}
		}
	},
	raiseEvent: function() {
		this.raiseEventBool = true;
	}
}