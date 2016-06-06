var Request = {
    // Constant webpage endpoints
    TO_FEATURE: "/rapid/feature/",
    TO_LAYER: "/rapid/layer/",
    TO_GEOVIEW: "/rapid/geoview/",
    TO_BASE: "/rapid/"
};

var geoViewStyle = {
        weight: 2,
        fillOpacity: 0,
        color: 'black',
        dashArray: '5,5'
    };

var geoViewGeometry = []; 

var control;

var gv;
    
function getGeoviews(geoViewsText, getLayers) {
    
    geoViewGeometry = [];
    
    geoViewList.innerHTML = '<li><h4>GeoViews</h4></li>';

    geoViews = { };
    
    views = JSON.parse(geoViewsText);
    var tokn = localStorage.getItem('token');

    // Grab individual geoview 
    for (var i = 0; i < views.length; i++) {
        ajaxCall(Request.TO_GEOVIEW + views[i].uid, function(response) {
            getGeoview(response, getLayers)});
        }
}

function getGeoview(geoViewText, getLayers) {
    
    view = JSON.parse(geoViewText);
    var tokn = localStorage.getItem('token');
    
    
    geoViews[view.descriptor] = view;

    var geoViewStyle = {
        weight: 2,
        fillOpacity: 0,
        color: 'black',
        dashArray: '5,5',
        clickable: false
    }

    geoViewGeometry.push(view.geom);

/////// Routine for creating list of GeoViews with nested associated layers /////////////////////////
        
        var geoViewListElement = document.createElement("LI");
        var geoViewListElementDiv = document.createElement('DIV');
        geoViewListElementDiv.id = view.uid;
        //geoViewListElementDiv.class = 'geoViewListElement';
        var descriptor = document.createTextNode(view.descriptor);
        var showIntersectingFeatures = document.createElement("BUTTON");
						    showIntersectingFeatures.type = 'button';
						    showIntersectingFeatures.id = view.uid + '_show';
                            showIntersectingFeatures.style.float = 'right';
                            showIntersectingFeatures.className = 'btn btn-default btn-xs';
						    showIntersectingFeatures.onclick = function () {
                                getFeaturesInGeoview(geoViewListElementDiv.id);
                                return false;
                            }
                            showIntersectingFeatures.value = 'Get Features';
                        var buttonText = document.createTextNode(view.descriptor);
                            showIntersectingFeatures.appendChild(buttonText);
        geoViewListElement.appendChild(descriptor);
        geoViewListElement.appendChild(showIntersectingFeatures);

        var ul = document.createElement("UL");
        ul.id = view.uid + '_layers';

        for (i = 0; i < view.layers.length; i++) {
            var liDiv = document.createElement("DIV");
            var li = document.createElement("LI");
            var descriptor = document.createTextNode(view.layers[i].descriptor);
            liDiv.id = view.layers[i].uid;
            //liDiv.class = 'layerListElement';

            li.appendChild(liDiv).appendChild(descriptor);
            ul.appendChild(li);
        }
        geoViewListElement.appendChild(ul);
        geoViewList.appendChild(geoViewListElement);

    if (getLayers) {
        // Create geoview object shell
        gview = {
            groupName : view.descriptor,
            expanded : true,
            layers : {}
        };

        // Iterate through layers in the GeoView
        for (var i = 0; i < view.layers.length; i++) { 

            // Create layer within geoview 
            var lyr = view.layers[i].descriptor;

            gview.layers[lyr] = new L.LayerGroup();

            var layerStyle = {
                weight: 2,
                color: '#'+(Math.random()*0xFFFFFF<<0).toString(16),
                opacity: 0.7,
                fillOpacity: 0.3
            };

            var layer = {
                group : gview.layers[lyr],
                style : layerStyle
            };

            var callback = function(featureText) {
                var feature = JSON.parse(featureText);

                // Constructing pop up string 
                var popUp = "";

                for (x in feature.properties) {
                    var str = x + " : " + feature.properties[x] + "<br>";
                    popUp += str;
                }

                // Use style in layer object and add geometry to layer group
                L.geoJson(feature, this.style).bindPopup(popUp).addTo(this.group);
            }.bind(layer);

            //Loop through features and adding them to the layer
            for ( var j = 0; j < view.layers[i].features.length; j++) {
                ajaxCall(Request.TO_FEATURE+view.layers[i].features[j]+"?token="+tokn, callback);
            }
        }
    // Add this geoview to overlays: an array used in the construction of the gui
    overlays.push(gview);
    }
}    

function ajaxCall(address, callback) {
    
    var response =  $.ajax({
        type: "GET",
        async: true,
        dataType : "text",
        url: address,
        beforeSend: function(xhr) {
            xhr.withCredentials = true;
        },
        success: callback,
        error: function(error) {
            console.error(error.statusText);               
        }
    });
    return response;
}

function getFeaturesInGeoview(uid) {
    console.log(uid);
    var response = $.ajax({
       url: Request.TO_GEOVIEW + uid + '/features/',
       dataType: 'json',
       success: function (data) {
           L.geoJson(data, {
               onEachFeature: constructPopup
           }).addTo(map);
       }
    })
}

function constructPopup(feature, layer) {
    var popupText = "";

    popupText += "Parent layer : " + feature.properties.layer + "\n";
    var props = JSON.parse(feature.properties.properties);

    for (x in props) {
        var str = x + " : " + props[x] + "<br>";
        popupText += str;
    }

    layer.bindPopup(popupText);
}

function loadGUI() {
    // Grabs the geoviews associated with the user's token
    ajaxCall(Request.TO_GEOVIEW+"?token="+localStorage.getItem('token'), function (response) {
        getGeoviews(response, true)});
    //test();
}
   
$(document).ajaxStop(function () {
    if (control !== undefined) {
        control.removeFrom(map);
    }
    if (gv != undefined) {
        map.removeLayer(gv);
        gv = undefined;
    }
        control = L.Control.styledLayerControl(baseMaps, overlays, options);
        gv = L.geoJson(geoViewGeometry, {style: geoViewStyle});
        gv.addTo(map);
        control.addTo(map);
})