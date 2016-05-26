var layers  = {};

var refreshLayers = function () {
	try {
			var oReq = new XMLHttpRequest();
			oReq.open("GET", Request.TO_LAYER);
			oReq.send();

			oReq.onreadystatechange = function() {
				if (oReq.readyState == 4 && oReq.status == 200) {                
					//console.log(oReq.responseText);
					var existingLayers = JSON.parse(oReq.responseText);
					layerList.innerHTML = "<li><h4>Available Layers</h4></li>";

					for (i = 0; i < existingLayers.length; i++) {
					    var uid = existingLayers[i].uid;
					    layers[existingLayers[i].descriptor] = existingLayers[i];
						var liDiv = document.createElement("DIV");
						var button = document.createElement("BUTTON");
						    button.type = 'button';
						    button.id = uid + '_add'; button.style.float = 'right';
						    button.onclick = function () {
                                getGeoViewInput(uid);
                                button.disabled = true;
                                return false;
						    };
						    button.value = 'Add';
						var buttonText = document.createTextNode('Add'); button.appendChild(buttonText);
						
						var li = document.createElement("LI");
						var public = '(public) ';
						if (existingLayers[i].is_public == false) {
							public = '(private) ';
						}
						var descriptor = document.createTextNode(existingLayers[i].descriptor + " " + public);
						var uid = existingLayers[i].uid;
						liDiv.id = uid + '_layer'; liDiv.style.width = '400px'; liDiv.style.display = 'inline-block'; liDiv.style.marginBottom = '5px';
						li.appendChild(liDiv).appendChild(descriptor);
						liDiv.appendChild(button);
						layerList.appendChild(li);
					}
				}
	
    		}
		}
		catch(err) {
			alert("There was an error!");
			messageDiv.innerHTML = err.message;
		}
}

function getGeoViewInput(l_uid) {
    var div = document.getElementById(l_uid + '_layer');
    var form = document.createElement('FORM'); form.id = l_uid + '_form';
    var selector = document.createElement('SELECT');
    selector.style.float = 'right'; selector.id = l_uid + '_selector';
    selector.onfocus = function () {
         document.getElementById(l_uid + '_add').disabled = false;
         document.getElementById(l_uid + '_add').onclick = function () {
             addLayerToGeoView(l_uid, selector.value);
             return false;
         }
         return false;
     }
    for (var geoView in geoViews) {
        var option = document.createElement('OPTION');
        var optionText = document.createTextNode(geoViews[geoView].descriptor);
        option.value = geoViews[geoView].uid;
        selector.appendChild(option).appendChild(optionText);
    }
    form.appendChild(selector);
    div.appendChild(form);
}

function addLayerToGeoView (l_uid, gv_uid) {
    //console.log(l_uid + ' ' + gv_uid);
    var form = document.getElementById(l_uid + '_form');
    var liDiv = document.getElementById(l_uid + '_layer');
    liDiv.removeChild(form);

    try {
    var oReq = new XMLHttpRequest();
        oReq.open("GET", Request.TO_GEOVIEW + 'addlayer/' + gv_uid + '/' + l_uid + '/?token=' + localStorage.getItem('token'));
        oReq.send();

        oReq.onreadystatechange = function() {
            if (oReq.readyState == 4 && oReq.status == 200) {                
                messageDiv.innerHTML = (JSON.parse(oReq.responseText).status);
                var button = document.getElementById(l_uid + '_add');
                button.onclick = function () {
                    getGeoViewInput(l_uid);
                    button.disabled = true;
                    return false;
                }
                ajaxCall(Request.TO_GEOVIEW+"?token="+localStorage.getItem('token'), function (response) {
                    getGeoviews(response, true)});
            }
        }
    }
    catch(err) {
			alert("There was an error!");
			messageDiv.innerHTML = err.message;
   }

}

function sendDataLayer (des, public, props) {

    var layer = {
        "des": "",
        "public": "",
        "props": { }
    }

    layer.des = des; layer.public = public; layer.props = props;

    try {
    var oReq = new XMLHttpRequest();
        oReq.open("POST", Request.TO_LAYER + '?token=' + localStorage.getItem('token'));
        oReq.send(JSON.stringify(layer));

        oReq.onreadystatechange = function() {
            if (oReq.readyState == 4 && oReq.status == 200) {                
                messageDiv.innerHTML = (JSON.parse(oReq.responseText).status);
                refreshLayers();
            }
        }
    }
    catch(err) {
			alert("There was an error!");
			messageDiv.innerHTML = err.message;
   }


} 
