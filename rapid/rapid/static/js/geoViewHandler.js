/*
** Injects coordinates from the drawn object into a JSON
** object formatted to be ingested by RAPID
*/
function translateGeoView (drawnItems, desc) {
	
	if (drawnItems.getLayers().length == 1) {
		
			/* Get geometries from the featureGroup as geoJSON  */
			var drawnItemsGeoJson = drawnItems.toGeoJSON();
			
			/* Shell for proper formatting for RAPID ingestion  */
			/* TODO:  Update RAPID to accept a valid geoJSON feature */
			var geoJsonToPost = {
				"geom": {
					"type": "Polygon",
					"coordinates": []
					},
				"des": "",
				"props": {}
			};
			
			/* Inject "geom" (geometry) into the shell */
			geoJsonToPost.geom = drawnItemsGeoJson.features[0].geometry;
			
			/* Injects "des" (description) from user input and/or scraping in wizard */
			geoJsonToPost.des = desc;
			
			/* TODO: Inject "props" (properties/metadata) from user input and/or scraping in wizard */

			return geoJsonToPost;
	}
	else if (drawnItems.getLayers().length > 1) {
		alert("RAPID can only accept one feature per GeoView.");
	}
	else {
		alert("You must first draw and save a GeoView.");
	}
}

/*
**  Adds GeoView to RAPID.  Takes a properly formatted GeoView JSON object.  Use translateGeoview() prior to calling addGeoView()
**  Globals token and TO_GEOVIEW must be properly defined.
*/
function sendGeoView (geoView) {
		try {

			var oReq = new XMLHttpRequest();
			oReq.open("POST", Request.TO_GEOVIEW);
			oReq.send(JSON.stringify(geoView));

			oReq.onreadystatechange = function() {
				if (oReq.readyState == 4 && oReq.status == 200) {                
					//refreshGeoViews();
					drawControl.removeFrom(map);
					drawnItems.clearLayers();
					drawButton.disabled = false;
					sendButton.disabled = true;
					ajaxCall(Request.TO_GEOVIEW+"?token="+localStorage.getItem('token'), function (response) {
        				getGeoviews(response, false)});
				}
    		}
		}
		catch(err) {
			messageDiv.innerHTML = err.message;
		}
}

function checkInput() {
    
    if (input.value == null || input.value == "") {
   		sendButton.disabled = true;
    }
    else {
    	sendButton.disabled = false;
    	return input.value;
    }
}

function addGeoView () {
	
	if (translateGeoView(drawnItems, desc)) {
		var desc = input.value;
		var geoView = translateGeoView(drawnItems, desc);
		sendGeoView(geoView);
	}
}

