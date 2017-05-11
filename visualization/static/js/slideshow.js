function slideShow() {

	// Arrays with the series of images to be shown
	overlays = [];
	textIndicators = [];
	translateIndicators = [];
	heightIndicators = [];
	thumbnailsImages = [];
	
	loader.raiseEvent();
	// We load all the images
	for(var ind = currentIndex; ind < image.length; ind = ind +1){
		loader.addLoading(true);
		if (boolWeather){
			if(allValues['cloud_height'] != undefined && allValues['cloud_height'].length > 0){
			    var thisHeightVal = allValues['cloud_height'][indexNearestValue(image[ind].time, allValues['cloud_height'])].value;
			} else {
			    var thisHeightVal = 1000;
			}
		} else {
			thisHeightVal = 1000;
		}
		
		textIndicators.push(formatTime(image[ind].time));
		translateIndicators.push("translate(" + x(image[ind].time ) + " ,0)");
		if(boolRadiosondeAM | boolRadiosondePM){
			heightIndicators.push("translate(0, " + (altitudesScale(thisHeightVal/1000) - heightRad) + " )");
		}
		imgTbId = 'imgTb' + ind;
		imgElem = $('<img>');
		imgElem.attr('id', imgTbId);
		imgElem.attr('src', image[ind].url_tn);
		imgElem.css('display', 'none');
		imgElem.css('position', 'absolute');
		$("#image-thumbnail").append(imgElem);
		thumbnailsImages.push(imgTbId);
		
		// Add the overlay as invisible
	    thisOverlay = new SkyPictureOverlay(image[ind].undistorted, imageCenter, thisHeightVal, false);
	    thisOverlay.setMap(map);
	    overlays.push(thisOverlay);
    }
	
	// Run the slideshow
	document.addEventListener("overlaysReady", function(){
		// Remove the currently selected image
		overlay.disappear();
		$("#imgTb").fadeOut(30);
	
		function start(){
			
			// Make the current overlay appear
			overlays[ind].appear();
			
			// Which will stop in half a second
			setTimeout(stop, 500);
			
			// Move the image indicator
			imageIndicatorText.text(textIndicators[ind]);
			imageIndicator.transition()
				.attr("transform", translateIndicators[ind])
				.duration(200);
			if(boolRadiosondeAM | boolRadiosondePM){
				heightIndicator.transition()
					.attr("transform", heightIndicators[ind])
					.duration(200);
			}
			$('#' + thumbnailsImages[ind]).fadeIn(30);
		}
		
		function stop(){
			overlays[ind].disappear();
			$('#' + thumbnailsImages[ind]).fadeOut(30);
			
			// Increment index
			ind = ind + 1;
			
			// Show next image
			if(ind < overlays.length){
				start();
			} else {
				// Or revert to currently selected image
				$("#imgTb").fadeIn(30);
				for(var j=0; j< overlays.length;j++){
					overlays[j].setMap(null);
				}
				imageIndicatorText.text(formatTime(image[currentIndex].time));
				imageIndicator.transition()
					.attr("transform", "translate(" + x(image[currentIndex].time ) + " ,0)")
					.duration(200);
				if(boolRadiosondeAM | boolRadiosondePM){
					heightIndicator.transition()
						.attr("transform", "translate(0, " + (altitudesScale(cloudHeightVal/1000) - heightRad) + " )")
						.duration(200);
				}
				overlay.appear();
			}
		}
		
		ind = 0;
		start();
		
	}, false);
}

$("#playimg").click(slideShow);