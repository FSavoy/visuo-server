var map;

/**
 * Expanding Google maps LatLng object for new point computation given point,
 * bearing and distance.
 */
Number.prototype.toRad = function() {
	return this * Math.PI / 180;
}

Number.prototype.toDeg = function() {
	return this * 180 / Math.PI;
}

google.maps.LatLng.prototype.destinationPoint = function(brng, dist) {
	// http://stackoverflow.com/questions/2637023/how-to-calculate-the-latlng-of-a-point-a-certain-distance-away-from-another#comment2651202_2637079
	dist = dist / 1000; // Input in meters, go to km
	dist = dist / 6371;  
	brng = brng.toRad();  

	var lat1 = this.lat().toRad(), lon1 = this.lng().toRad();

	var lat2 = Math.asin(Math.sin(lat1) * Math.cos(dist) + 
				Math.cos(lat1) * Math.sin(dist) * Math.cos(brng));

	var lon2 = lon1 + Math.atan2(Math.sin(brng) * Math.sin(dist) *
						Math.cos(lat1), 
						Math.cos(dist) - Math.sin(lat1) *
						Math.sin(lat2));

	if (isNaN(lat2) || isNaN(lon2)) return null;

	return new google.maps.LatLng(lat2.toDeg(), lon2.toDeg());
}



/**
 * Creating a custom overlay for google maps api
 */
SkyPictureOverlay.prototype = new google.maps.OverlayView();

// Constructor
function SkyPictureOverlay(image, imageCenter, cloud_height, visible) {
	if(typeof(visible)==='undefined') visible = true;
	  
	var diagonal_distance = cloud_height/Math.tan(0.21756061);
	  
	var imageBounds = new google.maps.LatLngBounds(
		imageCenter.destinationPoint(225, diagonal_distance),
		imageCenter.destinationPoint(45, diagonal_distance));
	
	// Initialize all properties.
	this.bounds_ = imageBounds;
	this.image_ = image;
	
	// Define a property to hold the image's div. We'll
	// actually create this div upon receipt of the onAdd()
	// method so we'll leave it null for now.
	this.div_ = null;
	
	// Indicates if the overlay is visible or not
	this.visible = visible;

	// Explicitly call setMap on this overlay.
	// this.setMap(map);
}

// onAdd is called when the map's panes are ready and the overlay has been
// added to the map.
SkyPictureOverlay.prototype.onAdd = function() {
	var div = document.createElement('div');
	div.style.borderStyle = 'none';
	div.style.borderWidth = '0px';
	div.style.position = 'absolute';
	div.style.zIndex = '6';
	if(this.visible){
		div.style.display = 'inline';
	} else {
		div.style.display = 'none';
	}

	// Create the img element and attach it to the div.
	var imgElem = document.createElement('img');
	var img = new Image();
	$(img).bind('load', function() {
		div.appendChild(imgElem);
		loader.removeLoading();
	});
	img.src = this.image_;
	imgElem.src = img.src;
	imgElem.style.width = '100%';
	imgElem.style.height = '100%';
	imgElem.style.position = 'absolute';

	this.div_ = div;

	// Add the element to the "overlayLayer" pane.
	var panes = this.getPanes();
	panes.overlayLayer.appendChild(div);
};
  
SkyPictureOverlay.prototype.draw = function() {
	// We use the south-west and north-east
	// coordinates of the overlay to peg it to the correct position and size.
	// To do this, we need to retrieve the projection from the overlay.
	var overlayProjection = this.getProjection();

	// Retrieve the south-west and north-east coordinates of this overlay
	// in LatLngs and convert them to pixel coordinates.
	// We'll use these coordinates to resize the div.
	var sw = overlayProjection.fromLatLngToDivPixel(this.bounds_.getSouthWest());
	var ne = overlayProjection.fromLatLngToDivPixel(this.bounds_.getNorthEast());

	// Resize the image's div to fit the indicated dimensions.
	var div = this.div_;
	div.style.left = sw.x + 'px';
	div.style.top = ne.y + 'px';
	div.style.width = (ne.x - sw.x) + 'px';
	div.style.height = (sw.y - ne.y) + 'px';
};

// The onRemove() method will be called automatically from the API if
// we ever set the overlay's map property to 'null'.
SkyPictureOverlay.prototype.onRemove = function() {
	this.div_.parentNode.removeChild(this.div_);
	this.div_ = null;
};

// Makes the overlay appear
SkyPictureOverlay.prototype.appear = function() {
	$(this.div_).fadeIn(30);
}

// Makes the overlay disappear
SkyPictureOverlay.prototype.disappear = function() {
	$(this.div_).fadeOut(30);
}

/**
 * Initialize google maps api
 */
var mapOptions = {
		center: imageCenter,
		zoom: 14,
		mapTypeId: 'satellite',
		disableDefaultUI: true
	};

function resizeMapCanevas(){
	document.getElementById("container").style.height = window.innerHeight + "px";
	document.getElementById("content").style.height= window.innerHeight - 140 + "px";
	document.getElementById("map-canevas").style.height= window.innerHeight - 200 + "px";
};

function initialize() {
	resizeMapCanevas();
	map = new google.maps.Map(document.getElementById("map-canevas"), mapOptions);
	
	loadImage(0);
};
google.maps.event.addDomListener(window, 'load', initialize);

window.onresize = function(event){
	resizeMapCanevas();
};