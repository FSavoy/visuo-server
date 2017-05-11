/**
 * Managing both data type selection forms
 */
 
// Returns the unit
function getUnit(text) {
	var regexBetweenParenthesis = /\((.+)\)/;
	var regres = regexBetweenParenthesis.exec(text);
	if(regres && regres.length == 2){
		return ' ' + regres[1];
	} else {
		return '';
	}
}

if(boolWeather){
	// Loading the data received by django
	var $formLeft = $("#dataSelectionFormLeft")
	$.each(items, function(key, value) {
		$formLeft.append($("<option></option>")
			.attr("value", value).text(key));
	});
	
	var $formRight = $("#dataSelectionFormRight")
	$.each(items, function(key, value) {
		$formRight.append($("<option></option>")
			.attr("value", value).text(key));
	});
	
	// Selecting the first and second element
	$formLeft.contents().eq(0).prop('selected', true);
	$formRight.contents().eq(1).prop('selected', true);
	
	// Loading the values and units
	var leftValues = allValues[$formLeft.val()];
	var rightValues = allValues[$formRight.val()];
	var leftUnit = getUnit($("#dataSelectionFormLeft :selected").text());
	var rightUnit = getUnit($("#dataSelectionFormRight :selected").text());
	
	
	// Reloads the graph when a selected value is changed
	$formLeft.change(function(){
		leftValues = allValues[$formLeft.val()];
		leftUnit = getUnit($("#dataSelectionFormLeft :selected").text());
		loadGraph();
	});
	
	$formRight.change(function(){
		rightValues = allValues[$formRight.val()];
		rightUnit = getUnit($("#dataSelectionFormRight :selected").text());
		loadGraph();
	});
} else {
	// If no weather data to show, hide the forms
	$("#dataSelectionFormLeft").fadeOut(0);
	$("#dataSelectionFormRight").fadeOut(0);
}

/**
 * Create the graph and modifies its size
 */

var margin = {top: 35, right: 70, bottom: 22, left: 70};

// The width of the page
var pageWidth = Math.max(Math.max(self.innerWidth || 0, document.documentElement.clientWidth || 0, document.body.clientWidth || 0), 1024);
var width = pageWidth - margin.left - margin.right - 290;

// The height depends on if there is data to show
if(boolWeather){
	var height = 130 - margin.top - margin.bottom;
} else {
	var height = 10;
}
    
// The main svg container
var svgContainer = d3.select("#weather-infos-content").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom);

// The container for the graph
var svg = svgContainer.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
   
// Adapting all the div's sizes
document.getElementById("container").style.height = window.innerHeight + "px";
document.getElementById("content").style.height= window.innerHeight - 140 + "px";
document.getElementById("map-canevas").style.height= window.innerHeight - 200 + "px";
document.getElementById("dataSelectionFormLeft").style.bottom= height + 35 + "px";
document.getElementById("dataSelectionFormRight").style.bottom= height + 35 + "px";
document.getElementById("playimg").style.bottom = height + 83 + "px";
document.getElementById("playimg").style.left = 60 + margin.left + width/2 + "px";


/**
 * Create the axis and scales
 */

// The bottom time axis
var x = d3.scaleTime()
	.range([0, width]);

var xAxis = d3.axisBottom(x)
 .tickFormat(d3.timeFormat('%H:%M'));

x.domain([parseTime("00:00:00"), parseTime("23:59:59")]);

var xAxisG = svg.append("g")
	.attr("class", "x axis")
	.attr("transform", "translate(0," + height + ")")
	.call(xAxis);

// Axis to plot data on both sides
if(boolWeather){
	var y1 = d3.scaleLinear()
		.range([height, 0]);
	    
	var y2 = d3.scaleLinear()
		.range([height, 0]);
	
	var y1Axis = d3.axisLeft()
		.ticks(6);
	    
	var y2Axis = d3.axisRight()
		.ticks(6);
		
	var leftAxis = svg.append("g")
		.attr("class", "y axis");
	      
	leftAxis.append("circle")
		.attr("class", "cicrleLeft")
		.attr("r", 4)
		.attr("cx", -60)
		.attr("cy", -22);
	      
	var rightAxis = svg.append("g")
		.attr("class", "y axis")
		.attr("transform", "translate(" + width + ",0)");
	      
	rightAxis.append("circle")
		.attr("class", "cicrleRight")
		.attr("r", 4)
		.attr("cx", 60)
		.attr("cy", -22);
}

/**
 * Plot the data
 */
if(boolWeather){
	
	// Line corresponding to data with the left axis
	var lineLeft = d3.line()
		.x(function(d) { return x(d.time); })
		.y(function(d) { return y1(d.value); });
	    
	// Line corresponding to data with the right axis
	var lineRight = d3.line()
		.x(function(d) { return x(d.time); })
		.y(function(d) { return y2(d.value); });
		
	var pathLeft = svg.append("path")
		.attr("class", "lineLeft");
	      
	var pathRight = svg.append("path")
		.attr("class", "lineRight");
}

if(boolWeather){
	loadGraph();
		
	// Reads and plots the data
	function loadGraph(){
		y1.domain(d3.extent(d3.extent(leftValues, function(d) { return d.value; })));
		y2.domain(d3.extent(d3.extent(rightValues, function(d) { return d.value; })));
	
		y1Axis.scale(y1);
		leftAxis.transition().duration(750).call(y1Axis);
		y2Axis.scale(y2);
		rightAxis.transition().duration(750).call(y2Axis);
	
		pathLeft.transition().duration(750).attr("d", lineLeft(leftValues));
		pathRight.transition().duration(750).attr("d", lineRight(rightValues));
	}
}

/**
 * Small red line for every available image
 */
var lines;
function drawSmallRedLines(){
	console.log('drawSmall lines');
	console.log('height ' + height);
	lines = svg.selectAll(".lineTimeOtherImages")
		.data(image);
	lines.enter().append('line').attr("class", "lineTimeOtherImages")
	.attr("x1", function(d){return x(d.time);})
	.attr("y1", height-5)
	.attr("x2", function(d){return x(d.time);})
	.attr("y2", height);
	lines.exit().remove();
}
drawSmallRedLines();


/**
 * The information box moving with the mouse
 */
var focus = svg.append("g")
	.style("display", "none");
	
// The red line indicating the iamge
var imageLine = focus.append("line")
	.attr("class", "lineTimeIndicator")
	.attr("x1", 0)
	.attr("y1", 0)
	.attr("x2", 0)
	.attr("y2", height);
		
// The moving box
if(boolWeather){
	
	var focusValuesTransform = focus.append("g");
	var focusValues = focusValuesTransform.append("g")
	
	// Size and rectangle around it
	var valuesBoxHeight = 43;
	var valuesBoxWidth = 95;
	focusValues.append("rect")
		.attr("class", "valuesBox")
		.attr("height", valuesBoxHeight)
		.attr("width", valuesBoxWidth);
	
	// The time indication text
	var timeValue = focusValues.append("text")
		.attr("x", valuesBoxWidth/2)
		.attr("y", 21)
		.attr("dy", "-.71em")
		.style("text-anchor", "middle")
		.style("font-weight", "bold");
	   		
	// Left data circle
	focusValues.append("circle")
		.attr("class", "cicrleLeft")
		.attr("cx", 9)
		.attr("cy", 22.5)
		.attr("r", 4);
	   		
	// Left data value
	var leftValue = focusValues.append("text")
		.attr("x", 17)
		.attr("y", 23)
		.attr("dy", ".29em");
	   		
	// Right data circle
	focusValues.append("circle")
		.attr("class", "cicrleRight")
		.attr("cx", 9)
		.attr("cy", 33.5)
		.attr("r", 4);
	   		
	// Right data value
	var rightValue = focusValues.append("text")
		.attr("x", 17)
		.attr("y", 34)
		.attr("dy", ".29em");
	
	// The circles moving on the lines with the data
	var focusCircles = focus.append("g");
	
	var focusCircleLeft = focusCircles.append("circle")
		.attr("class", "cicrleLeft")
		.attr("r", 4);
			
	var focusCircleRight = focusCircles.append("circle")
		.attr("class", "cicrleRight")
		.attr("r", 4);
}
	
// Overlay rectangle to catch mouse events
var overlayRect = svg.append("rect")
	.attr("class", "overlay")
	.attr("width", width)
	.attr("height", height)
	.on("mouseover", function() { focus.style("display", "inline"); })
	.on("mouseout", function() { focus.style("display", "none"); })
	.on("mousemove", mousemove)
	.on("click", click);
	
// Get the index of the nearest image when clicking on the graph
function indexNearestImage(timePos) {
	var bisectTimeImages = d3.bisector(function(d) { return d.time; }).left;
	var i = bisectTimeImages(image, timePos, 1, image.length-1);
	var d0 = image[i - 1];
	var d1 = image[i];
	if (typeof d1 !== 'undefined') {
	    return timePos - d0.time > d1.time - timePos ? i : i-1;
	} else {
		return i-1;
	}
}

// Get the index of the nearest data point when clicking on the graph
function indexNearestValue(timePos, values) {
	var bisectTime = d3.bisector(function(d) { return d.time; }).left;
	var i = bisectTime(values, timePos, 1, values.length - 1);
	var d0 = values[i - 1];
	var d1 = values[i];
	if (typeof d1 !== 'undefined') {
	    return timePos - d0.time > d1.time - timePos ? i : i-1;
	} else {
		return i-1;
	}
}

// Boolean indicating if the focus box should be on the left of the mouse
// instead of the right
var atTheEnd = false;

// Modifies the focus box when the mouse moves
function mousemove() {
	var x0 = x.invert(d3.mouse(this)[0]);
	var d = image[indexNearestImage(x0)];
	imageLine.attr("transform", "translate(" + x(d.time) + ",0)");
	
	if(boolWeather){
		// Update the position of the box
		focusCircles.attr("transform", "translate(" + d3.mouse(this)[0] + ",0)");
		var focusValuesXtrans = 10;
		var focusValuesXtransAtTheEnd = - 20 - valuesBoxWidth;
		var focusValuesYtrans = height/2 - valuesBoxHeight/2;
		focusValuesTransform.attr("transform", "translate(" + (d3.mouse(this)[0] + focusValuesXtrans) + "," + focusValuesYtrans +")");

		if(!atTheEnd && ((width - x(x0)) < (valuesBoxWidth + 10))){
			atTheEnd = true;
			focusValues.transition().attr("transform", "translate(" + focusValuesXtransAtTheEnd + ",0)");
		}
		
		if(atTheEnd && ((width - x(x0)) > (valuesBoxWidth + 10))){
			atTheEnd = false;
			focusValues.transition().attr("transform", "translate(0,0)");
		}
		timeValue.text(formatTime(x0));
		
		// Modifies the text and the circle from the left axis
		var thisLeftValue = leftValues[indexNearestValue(x0, leftValues)];
		focusCircleLeft.attr("transform", "translate(0," + y1(thisLeftValue.value) + ")");
		leftValue.text(thisLeftValue.value + leftUnit);
		
		// Modifies the text and the circle from the right axis
		var thisRightValue = rightValues[indexNearestValue(x0, rightValues)];
		focusCircleRight.attr("transform", "translate(0," + y2(thisRightValue.value) + ")");
		rightValue.text(thisRightValue.value + rightUnit);
	}
}

// Load the nearest image when clicking on the graph
function click() {
	var x0 = x.invert(d3.mouse(this)[0]);
	loadImage(indexNearestImage(x0));
}

/**
 * Loading the current image Indicator about current image on the axis
 */
currentImageIndex = 0

var imageIndicator = svg.append("g")

var imageIndicatorLine = imageIndicator.append("line")
	.attr("class", "lineTime")
	.attr("x1", 0)
	.attr("y1", 0)
	.attr("x2", 0)
	.attr("y2", height);
  		
var imageIndicatorRect = imageIndicator.append("rect")
	.attr("class", "timeRect")
	.attr("height", 14)
	.attr("width", 64)
	.attr("x", -32)
	.attr("y", height + 7);
   		
var imageIndicatorText = imageIndicator.append("text")
	.attr("x", 0)
	.attr("y", height + 9)
	.attr("dy", ".71em")
	.style("text-anchor", "middle")
	.style("font-weight", "bold");

// The cloud base height value
var cloudHeightVal;

// Index of the currently displayed image
var currentIndex;

// The skypicture overlay object
var overlay;

function loadImage(imageIndex){
	// Enable the loader
	loader.addLoading();
	currentIndex = imageIndex;
	
	// Update the cloud base height
	if(boolWeather){
		if(allValues['cloud_height'] != undefined && allValues['cloud_height'].length > 0){
		    cloudHeightVal = allValues['cloud_height'][indexNearestValue(image[imageIndex].time, allValues['cloud_height'])].value;
		} else {
		    cloudHeightVal = 1000;
		}
	} else {
		cloudHeightVal = 1000;
	}
	
	// Update the text in the red box
	imageIndicatorText.text(formatTime(image[imageIndex].time));
	
	// Moves the image indicator to the new location
	imageIndicator.transition()
		.attr("transform", "translate(" + x(image[imageIndex].time ) + " ,0)")
		.duration(1000);
	if (boolRadiosondeAM | boolRadiosondePM){
		heightIndicator.transition()
			.attr("transform", "translate(0, " + (altitudesScale(cloudHeightVal/1000) - heightRad) + " )")
			.duration(1000);
	}
		
	// Update the image thumbnail
	$("#imgTb").attr("src", image[imageIndex].url_tn);
	
	// Add the sky picture as an overlay on the map
	if(overlay != null){
		overlay.setMap(null);
	}
    overlay = new SkyPictureOverlay(image[imageIndex].undistorted, imageCenter, cloudHeightVal);
    overlay.setMap(map);
}


/**
 * Modifying the size of the elements when window resizes
 */
function onresizeWeather(event) {
	 
	// Adapting the width of the container
	pageWidth = Math.max(Math.max(self.innerWidth || 0, document.documentElement.clientWidth || 0, document.body.clientWidth || 0), 1024);
	width = pageWidth - margin.left - margin.right - 290;
	if(boolWeather){
		height = 130 - margin.top - margin.bottom;
	} else {
		height = 10;
	}
	
	svgContainer.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom);
	
	// Updating the time axis
	x.range([0, width])
	xAxisG.call(xAxis);
	xAxisG.attr("transform", "translate(0," + height + ")");
	
	if(boolWeather){
		// Resize the y axis
		y1.range([height, 0]);
		leftAxis.call(y1Axis);
		y2.range([height, 0]);
		rightAxis.call(y2Axis);
		rightAxis.attr("transform", "translate(" + width + ",0)");
		
		// Redraw the lines
		lineLeft.x(function(d) { return x(d.time); })
			.y(function(d) { return y1(d.value); });
		lineRight.x(function(d) { return x(d.time); })
			.y(function(d) { return y2(d.value); });
		
		y1.domain(d3.extent(d3.extent(leftValues, function(d) { return d.value; })));
		y2.domain(d3.extent(d3.extent(rightValues, function(d) { return d.value; })));
		
		pathLeft.attr("d", lineLeft(leftValues));
		pathRight.attr("d", lineRight(rightValues));
		overlayRect.attr("width", width).attr("height", height);
		
		imageIndicatorLine.attr("y2", height);
		imageIndicatorRect.attr("y", height + 7);
		imageIndicatorText.attr("y", height + 9);
		imageIndicator.attr("transform", "translate(" + x(image[currentIndex].time ) + " ,0)");
		
		drawSmallRedLines();

		imageLine.attr("y2", height);
	}
	
	// Updating all the div's dimensions
	document.getElementById("container").style.height = window.innerHeight + "px";
	document.getElementById("content").style.height= window.innerHeight - 140 + "px";
	document.getElementById("map-canevas").style.height= window.innerHeight - 200 + "px";
	document.getElementById("dataSelectionFormLeft").style.bottom= height + 35 + "px";
	document.getElementById("dataSelectionFormRight").style.bottom= height + 35 + "px";
	document.getElementById("playimg").style.bottom = height + 83 + "px";
	document.getElementById("playimg").style.left = 60 + margin.left + width/2 + "px";
}







