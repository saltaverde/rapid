
var TO_GEOVIEW = "http://129.65.220.3:8000/rapid/geoview/";

/* JUST FOR THE TIME BEING!!! */
var tokens = {
	"Austin":"7ac00dda68de50bb74b6bdd1c0448f0a6579e8d2",
	"Alexa":"", 
	"Default": "97e3278c087bab2af8771b86df55b7419acf56d3",
	"MDA": "abf19f5ee6084794e4abf616e60115bd30b04551",
	"CCORE": "6734d62ec60a4d480fc52a8a92031f0b203fe477"
};

var token = "?token=" + tokens.CCORE;

/*
** Injects coordinates from the drawn object into a JSON
** object formatted to be ingested by RAPID
*/
function translateGeoView (drawnItems, desc) {
	
	if (drawnItems.getLayers().length == 1) {
		
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
			oReq.open("POST", TO_GEOVIEW + token);
			oReq.send(JSON.stringify(geoView));

			oReq.onreadystatechange = function() {
				if (oReq.readyState == 4 && oReq.status == 200) {                
					refreshGeoViews(token);
				}
    		}
		}
		catch(err) {
			messageDiv.innerHTML = err.message;
		}
	
}

function getGeoViewDesc() {
    var desc = prompt("Enter a descriptive name for this GeoView:", "");
    
    if (desc == null || desc == "") {
   		getGeoViewDesc();
    }
    else {
    	return desc;
    }
}

function addGeoView () {
	
	if (translateGeoView(drawnItems, desc)) {
		var desc = getGeoViewDesc();
		var geoView = translateGeoView(drawnItems, desc);
		sendGeoView(geoView);
	}
}

function refreshGeoViews (token) {
	try {
			var oReq = new XMLHttpRequest();
			oReq.open("GET", TO_GEOVIEW + token);
			oReq.send();

			oReq.onreadystatechange = function() {
				if (oReq.readyState == 4 && oReq.status == 200) {                
					existingGeoViews = JSON.parse(oReq.responseText);
					geoViewList.innerHTML = "<li><h4>Existing GeoViews</h4></li>";
					for (i = 0; i < existingGeoViews.length; i++) {
						var liDiv = document.createElement("DIV");
						var li = document.createElement("LI");
						var descriptor = document.createTextNode(existingGeoViews[i].descriptor);
						var uid = existingGeoViews[i].uid;
						li.id = uid;
						li.appendChild(liDiv).appendChild(descriptor);
						//li.appendChild(descriptor);
						document.getElementById('geoViewList').appendChild(li);
					}
				}
    		}
			
		}
		catch(err) {
			messageDiv.innerHTML = err.message;
		}
}

