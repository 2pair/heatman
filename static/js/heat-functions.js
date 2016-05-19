"use strict";

// reads in the data we received from the server and updates the heat layer
function updateHeatLayer(resp, heatLayer) {
    var jsonObj = JSON.parse(resp.responseText);    
   
    if (jsonObj.points != null) {
        heatLayer.setLatLngs(jsonObj.points);   
    }
}
