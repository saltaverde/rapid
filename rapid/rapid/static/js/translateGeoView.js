/*
** Injects coordinates from the drawn object into a JSON
** object formatted to be ingested by RAPID
*/
var translateGeoview = function (drawnItems) {
	/* Get geometries from the featureGroup as geoJSON  */
	drawnItemsGeoJson = drawnItems.toGeoJSON();
	
	/* Shell for proper formatting for RAPID ingestion  */
	/* TODO:  Update RAPID to accept a valid geoJSON feature */
	geoJsonToPost = {
		"geom": {
			"type": "Polygon",
			"coordinates": []
			},
		"des": "",
		"props": {}
	};
	
	/* Inject "geom" (geometry) into the shell */
	geoJsonToPost.geom = drawnItemsGeoJson.features[0].geometry;
	
	/* TODO: Inject "des" (description) from user input and/or scraping in wizard */
	
	/* TODO: Inject "props" (properties/metadata) from user input and/or scraping in wizard */

	return geoJsonToPost;
}

/*
**  Adds GeoView to RAPID.  Takes a properly formatted GeoView JSON object.  Use translateGeoview() prior to calling addGeoView()
**  Globals token and TO_GEOVIEW must be properly defined.
*/
var addGeoView = function (geoView) {
	
	if (geoView.features.length == 0) {
		alert("There is no defined GeoView to send.");
	}
	else if (geoView.features.length > 1) {
		alert("There are more than one GeoView features defined. RAPID can only accept one new GeoView at a time.");
	}
	else {
		try {
			var oReq = new XMLHttpRequest();
			oReq.open("POST", TO_GEOVIEW + token);
			oReq.send(JSON.stringify(geoView));
		}
		catch(err) {
			alert(err.message)
		}
	}
}
