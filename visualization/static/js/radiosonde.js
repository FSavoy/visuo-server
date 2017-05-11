/**
 * Creation of the containers
 */

// Margins of the graph within the div
var marginRad = {top: 15, right: 5, bottom: 85, left: 5};
var leftAxisMargin = 23;

// Size of the graph
var widthRad = 125 - marginRad.left - marginRad.right;
var heightRad = window.innerHeight - marginRad.top - marginRad.bottom - 290;
    
// The global container
var svgRadContainer = d3.select("#radiosonde-infos-content").append("svg")
	.attr("width", widthRad + marginRad.left + marginRad.right)
	.attr("height", heightRad + marginRad.top + marginRad.bottom);
	
// The container for graph and axis
var svgRad = svgRadContainer.append("g")
	.attr("transform", "translate(" + marginRad.left + "," + marginRad.top + ")");

// The container for the graph
var graph = svgRad.append("g")
	.attr("transform", "translate(" + leftAxisMargin + ", 0)");

/**
 * The selection form to choose data to show
 */

// Appending all the values (from django itemsRad value)
var $formRad = $("#radiosondeSelectionForm")
$.each(itemsRad, function(key, value) {
	$formRad.append($("<option></option>")
		.attr("value", value).text(key));
});

// Select the first one
$formRad.contents().eq(0).prop('selected', true);

// Extracts the unit from a "value (unit)" string
function getUnit(text) {
	var regexBetweenParenthesis = /\((.+)\)/;
	var regres = regexBetweenParenthesis.exec(text);
	if(regres && regres.length == 2){
		return ' ' + regres[1];
	} else {
		return '';
	}
}

// Which data to be plotted
var toPlot = $formRad.val();

// The unit of the data to be plotted
var radUnit = getUnit($("#radiosondeSelectionForm :selected").text());

// Reloading the graph when the form value changes
$formRad.change(function(){
	toPlot = $formRad.val();
	radUnit = getUnit($("#radiosondeSelectionForm :selected").text());
	radLoadGraph();
});

/**
 * Creation the axis and scales
 */

// The scale for plotting the data (altitude of the radiosonde balloon)
var altitudesScale = d3.scaleLinear()
	.range([heightRad, 0]);
	
// The scale at the bottom for the values colormap
var relhScale = d3.scaleLinear()
	.range(["steelblue", "brown"]);
var relhScaleNumbers = d3.scaleLinear()
	.range([0, widthRad]);

// Getting the domain of the altitude scale (afternoon data if no morning launch)
if(boolRadiosondeAM){
	altitudesScale.domain(d3.extent(arrAllValuesRadAM['HGHT']));
} else {
	altitudesScale.domain(d3.extent(arrAllValuesRadPM['HGHT']));
}

// The altitude axis
var yAxis = d3.axisLeft(altitudesScale);

var axisRadiosonde = graph.append("g")
	.attr("class", "y axis")
	.call(yAxis);

graph.append("text")
	.attr("y", 6)
	.attr("dy", ".71em")
	.attr("transform", "rotate(-90)")
	.style("text-anchor", "end")
	.text("Altitude [km]");
	
// The bottom axis for the colormap
var colorAxis = d3.axisBottom(relhScaleNumbers)
	.ticks(3);

var axisColor = svgRad.append("g")
	.attr("transform", "translate(0," + (heightRad + 21) + ")")
	.attr("class", "x axis")
	.call(colorAxis);


/**
 * Plot the data
 */

// The corresponding height for each pixel in the graph
var heightPixels = d3.range(heightRad+1);

// The container for the main graphs
var heatMapCloudLayer = graph.append('g');

// The containers for showing the detected clouds with SU model
var ticksLayer = graph.append('g');

// Returns the nearest radiosonde measurement given the altitude of a pixel
function indexNearestRadiosonde(heightPos, values) {
	var bisectRadMeasurements = d3.bisector(function(d) { return d.height; }).left;
	var i = bisectRadMeasurements(values, heightPos, 1, values.length - 1);
	var d0 = values[i - 1];
	var d1 = values[i];
	return heightPos - d0.height > d1.height - heightPos ? i : i-1;
}

// Creating the graphs for morning measurements (needs to be called again when the windows changes size)
function drawGraphsAM(){
	
	// Creating one line per pixel in the main graph
	var heatMapAM = heatMapCloudLayer.selectAll(".heatmapAM")
		.data(heightPixels);
		
	// Adding one line for each altitude pixel
	heatMapAM.enter().append('line').attr("class", "heatmapAM")
	.attr("x1", 35)
	.attr("y1", function(d){return d;})
	.attr("x2", 55)
	.attr("y2", function(d){return d;})
	.attr("stroke-width", 1)
	.attr("fill", "none")
	.style("shape-rendering", "crispEdges");
	heatMapAM.exit().remove();

	// Creating one line per pixel in the cloud detection graph
	var cloudsAM = heatMapCloudLayer.selectAll(".cloudsAM")
		.data(heightPixels);
	
	// Displaying the line blue or white depending on the clouds data
	cloudsAM.enter().append('line').attr("class", "cloudsAM")
	.attr("x1", 30)
	.attr("y1", function(d){return d;})
	.attr("x2", 35)
	.attr("y2", function(d){return d;})
	.attr("stroke", function(d) {
		var altitudePos = altitudesScale.invert(d);
		var radIndex = indexNearestRadiosonde(altitudePos, allValuesRadAM['clouds']);
		if(arrAllValuesRadAM['clouds'][radIndex] == 1){
			return "blue";
		} else {
			return "white";
		}
	})
	.attr("stroke-width", 1)
	.attr("fill", "none")
	.style("shape-rendering", "crispEdges");
	cloudsAM.exit().remove();
}

// Creating the morning graphs 
if(boolRadiosondeAM){
	drawGraphsAM();
}

function drawGraphsPM(){
	
	// Creating one line per pixel in the main graph
	var heatMapPM = heatMapCloudLayer.selectAll(".heatmapPM")
		.data(heightPixels);
		
	// Adding one line for each altitude pixel
	heatMapPM.enter().append('line').attr("class", "heatmapPM")
	.attr("x1", 70)
	.attr("y1", function(d){return d;})
	.attr("x2", 90)
	.attr("y2", function(d){return d;})
	.attr("stroke-width", 1)
	.attr("fill", "none")
	.style("shape-rendering", "crispEdges");;
	heatMapPM.exit().remove();

	// Creating one line per pixel in the cloud detection graph
	var cloudsPM = heatMapCloudLayer.selectAll(".cloudsPM")
		.data(heightPixels);
	
	// Displaying the line blue or white depending on the clouds data
	cloudsPM.enter().append('line').attr("class", "cloudsPM")
	.attr("x1", 65)
	.attr("y1", function(d){return d;})
	.attr("x2", 70)
	.attr("y2", function(d){return d;})
	.attr("stroke", function(d) {
		var altitudePos = altitudesScale.invert(d);
		var radIndex = indexNearestRadiosonde(altitudePos, allValuesRadPM['clouds']);
		if(arrAllValuesRadPM['clouds'][radIndex] == 1){
			return "blue";
		} else {
			return "white";
		}
	})
	.attr("stroke-width", 1)
	.attr("fill", "none")
	.style("shape-rendering", "crispEdges");;
	cloudsPM.exit().remove();
}

// Creating the evening graphs 
if(boolRadiosondePM){
	drawGraphsPM();
}

// The line indicating the altitude of the cloud base height of the shown image
var heightIndicator = svgRad.append("line")
	.attr("class", "lineTime")
	.attr("x1", 0)
	.attr("y1", heightRad)
	.attr("x2", widthRad)
	.attr("y2", heightRad);

/**
 * Color scale and legends
 */
 	
var widthPixels = d3.range(widthRad+1);
	
var heatMapScale = svgRad.selectAll(".heatMapScale")
	.data(widthPixels)
	.enter().append('line')
	.attr("x1", function(d){return d;})
	.attr("y1", heightRad + 10)
	.attr("x2", function(d){return d;})
	.attr("y2", heightRad + 20)
	.attr("stroke", function(d) {
			var color = relhScaleNumbers.invert(d);
			return relhScale(color);
		})
	.attr("stroke-width", 1)
	.attr("fill", "none")
	.style("shape-rendering", "crispEdges");

// Function modyfing the ranges and colors of the main graphs according to data
radLoadGraph();
function radLoadGraph(){
	
	// Get the extend of the data based on the available measurements
	if (!boolRadiosondeAM){
		relhScale.domain(d3.extent(allValuesRadPM[toPlot], function(d){ return d.value; }));
		relhScaleNumbers.domain(d3.extent(allValuesRadPM[toPlot], function(d){ return d.value; }));
	} else if(!boolRadiosondePM){
		relhScale.domain(d3.extent(allValuesRadAM[toPlot], function(d){ return d.value; }));
		relhScaleNumbers.domain(d3.extent(allValuesRadAM[toPlot], function(d){ return d.value; }));
	} else {
		var extentsRad = [d3.extent(allValuesRadAM[toPlot], function(d){ return d.value; }), d3.extent(allValuesRadPM[toPlot], function(d){ return d.value; })];
		relhScale.domain([d3.min(extentsRad, function(d) { return d[0]; }), d3.max(extentsRad, function(d) { return d[1]; })]);
		relhScaleNumbers.domain([d3.min(extentsRad, function(d) { return d[0]; }), d3.max(extentsRad, function(d) { return d[1]; })]);
	}

	// Modify the stroke color as a function of the data
	if (boolRadiosondeAM){
		heatMapCloudLayer.selectAll(".heatmapAM").transition().duration(750)
		.attr("stroke", function(d) {
			var heightPos = altitudesScale.invert(d);
			var radIndex = indexNearestRadiosonde(heightPos, allValuesRadAM[toPlot]);
			return relhScale(allValuesRadAM[toPlot][radIndex].value);
		});
	}

	if (boolRadiosondePM){
		heatMapCloudLayer.selectAll(".heatmapPM").transition().duration(750)
		.attr("stroke", function(d) {
			var heightPos = altitudesScale.invert(d);
			var radIndex = indexNearestRadiosonde(heightPos, allValuesRadPM[toPlot]);
			return relhScale(allValuesRadPM[toPlot][radIndex].value);
		});
	}
		
	// Change the colormap axis with new data
	axisColor.transition().duration(750).call(colorAxis);
	
	// Displaying one tick for each measurement
	if (boolRadiosondeAM){
		var ticksAM = ticksLayer.selectAll(".ticksAM")
			.data(allSamplesRadAM[toPlot].filter(function(d) {return d < 18000;}));
		ticksAM.enter().append('line').attr("class", "ticksAM")
		.transition().duration(750)
		.attr("x1", 50)
		.attr("y1", function(d){return altitudesScale(d/1000);})
		.attr("x2", 55)
		.attr("y2", function(d){return altitudesScale(d/1000);})
		.attr("stroke", "black")
		.attr("stroke-width", 1)
		.attr("fill", "none")
		.style("shape-rendering", "crispEdges")
		.style("z-index", "10");;
		ticksAM.exit().remove();
	}
	
	if (boolRadiosondePM){
		var ticksPM = ticksLayer.selectAll(".ticksPM")
			.data(allSamplesRadPM[toPlot].filter(function(d) {return d < 18000;}))
		ticksPM.enter().append('line').attr("class", "ticksPM")
		.transition().duration(750)
		.attr("x1", 85)
		.attr("y1", function(d){return altitudesScale(d/1000);})
		.attr("x2", 90)
		.attr("y2", function(d){return altitudesScale(d/1000);})
		.attr("stroke", "black")
		.attr("stroke-width", 1)
		.attr("fill", "none")
		.style("shape-rendering", "crispEdges");;
		ticksPM.exit().remove();
	}
}

/**
 * Legends
 */

// AM text label
graph.append('text')
	.attr("transform", "translate(45, -5)")
	.style("text-anchor", "middle")
	.text("AM");

// PM text label
graph.append('text')
	.attr("transform", "translate(80, -5)")
	.style("text-anchor", "middle")
	.text("PM");

// SU rectangle and text label
var SUrect = svgRad.append('rect')
	.attr("x", 0)
	.attr("y", -10)
	.attr("width", 5)
	.attr("height", 10)
	.attr("transform", "translate(-2," + (heightRad + 83) + ")")
	.style("fill", 'blue');

var SUtext = svgRad.append('text')
	.attr("transform", "translate(" + (widthRad/2 + 5) + "," + (heightRad + 83) + ")")
	.style("text-anchor", "middle")
	.text("Clouds (SU 91)");


/**
 * Information box moving with the mouse
 */
// Container for the information box (spanning the whole box)
var focusRad = svgRad.append("g")
	.style("display", "none");
	
// The container of the box itself
var focusValuesRad = focusRad.append("g");

// The size of the information box
var valuesBoxHeight = 43;
var valuesBoxWidth = 120;

// Appending the outer rectangle
focusValuesRad.append("rect")
	.attr("class", "valuesBox")
	.attr("height", valuesBoxHeight)
	.attr("width", valuesBoxWidth);

var altitudeValue = focusValuesRad.append("text")
	.attr("x", valuesBoxWidth/2)
	.attr("y", 21)
	.attr("dy", "-.71em")
	.style("text-anchor", "middle")
	.style("font-weight", "bold");
	
// Color circle for the AM value
if (boolRadiosondeAM){
	var relhAMCircle = focusValuesRad.append("circle")
		.attr("cx", 9)
		.attr("cy", 22.5)
		.attr("r", 4);
	   		
	var relhAMValue = focusValuesRad.append("text")
		.attr("x", 17)
		.attr("y", 23)
		.attr("dy", ".29em");
}
   		
// Color circle for the PM value
if (boolRadiosondePM){
	var relhPMCircle = focusValuesRad.append("circle")
		.attr("cx", 9)
		.attr("cy", 33.5)
		.attr("r", 4);
	   		
	var relhPMValue = focusValuesRad.append("text")
		.attr("x", 17)
		.attr("y", 34)
		.attr("dy", ".29em");
}
	
// Line indicating the location of the mouse
focusRad.append("line")
	.attr("class", "lineTimeIndicator")
	.attr("x1", 0)
	.attr("y1", 0)
	.attr("x2", widthRad)
	.attr("y2", 0);
	
// Adding the overlay and changing it depending on mouse action
var radOverlay = svgRad.append("rect")
	.attr("class", "overlay")
	.attr("width", widthRad)
	.attr("height", heightRad)
	.on("mouseover", function() { focusRad.style("display", "inline"); })
	.on("mouseout", function() { focusRad.style("display", "none"); })
	.on("mousemove", mousemoveRad);

// Function modifying the information box when the mouse moves
function mousemoveRad() {
	// Get the y position on the altitude scale
	var y0 = altitudesScale.invert(d3.mouse(this)[1]);
	
	// Updating the morning value
	if(boolRadiosondeAM){
		var dAM = allValuesRadAM[toPlot][indexNearestRadiosonde(y0, allValuesRadAM[toPlot])];
		altitudeValue.text(dAM.height.toPrecision(4) + " km");
		relhAMValue.text("AM: " + dAM.value.toPrecision(3) + radUnit);
		relhAMCircle.style("fill", relhScale(dAM.value));
		focusRad.attr("transform", "translate(0," + altitudesScale(dAM.height) + ")");
	}
	
	// Updating the afernoon value
	if(boolRadiosondePM){
		var dPM = allValuesRadPM[toPlot][indexNearestRadiosonde(y0, allValuesRadPM[toPlot])];
		altitudeValue.text(dPM.height.toPrecision(4) + " km");
		relhPMValue.text("PM: " + dPM.value.toPrecision(3) + radUnit);
		relhPMCircle.style("fill", relhScale(dPM.value));
		focusRad.attr("transform", "translate(0," + altitudesScale(dPM.height) + ")");
	}
	
	// Moving the box to the new location
	var focusValuesXtrans = widthRad/2 - valuesBoxWidth/2;
	var focusValuesYtrans = 10;
	focusValuesRad.attr("transform", "translate(" + focusValuesXtrans + "," + focusValuesYtrans +")");
}

// Called when the window resizes
function onresizeRadiosonde(event){
	
	// The new dimensions and margins
	var widthRad = 125 - marginRad.left - marginRad.right;
	var heightRad = window.innerHeight - marginRad.top - marginRad.bottom - 285;
    
	// Updating the size of the containers
	svgRadContainer.attr("width", widthRad + marginRad.left + marginRad.right)
		.attr("height", heightRad + marginRad.top + marginRad.bottom);
	radOverlay.attr("width", widthRad).attr("height", heightRad);	
	
	axisColor.attr("transform", "translate(0," + (heightRad + 21) + ")");
	SUrect.attr("transform", "translate(-2," + (heightRad + 80) + ")");
	SUtext.attr("transform", "translate(" + (widthRad/2 + 5) + "," + (heightRad + 80) + ")");
	heatMapScale.attr("y1", heightRad + 10).attr("y2", heightRad + 20);

	// Updating the ticks indicating the measurements
	heightIndicator.attr("y1", heightRad).attr("y2", heightRad);
	altitudesScale.range([heightRad, 0]);
	
	// Updating the axis scales
	yAxis.scale(altitudesScale);
	axisRadiosonde.call(yAxis);
	
	heightPixels = d3.range(heightRad+1);
	
	// Redrawing the moring graph
	if(boolRadiosondeAM){
		drawGraphsAM();
		heatMapCloudLayer.selectAll(".heatmapAM")
			.attr("stroke", function(d) {
				var heightPos = altitudesScale.invert(d);
				var radIndex = indexNearestRadiosonde(heightPos, allValuesRadAM[toPlot]);
				return relhScale(allValuesRadAM[toPlot][radIndex].value);
			});
			
		ticksLayer.selectAll(".ticksAM")
			.attr("y1", function(d){return altitudesScale(d/1000);})
			.attr("y2", function(d){return altitudesScale(d/1000);});
	}

	// Redrawing the afternoon graph
	if(boolRadiosondePM){
		drawGraphsPM();
		heatMapCloudLayer.selectAll(".heatmapPM")
			.attr("stroke", function(d) {
				var heightPos = altitudesScale.invert(d);
				var radIndex = indexNearestRadiosonde(heightPos, allValuesRadPM[toPlot]);
				return relhScale(allValuesRadPM[toPlot][radIndex].value);
			});
			
		ticksLayer.selectAll(".ticksPM")
			.attr("y1", function(d){return altitudesScale(d/1000);})
			.attr("y2", function(d){return altitudesScale(d/1000);});
	}
}


