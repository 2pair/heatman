// requires leaflet.js  --  http://leafletjs.com/
"use strict";

// gets the queries to send to the server
// returns an object consisting of the five queries
function constructQueries() {
    // how much data outside of the view port we request
    // allows for heat blobs to meld into/out of the view port
    var grow = 1.08; // times original size
    var bounds = pad(map.getBounds(), grow);
        
    var northWestBound = bounds.getNorthWest();
    var southEastBound = bounds.getSouthEast();
   
    var queries = {
        nw_lat: northWestBound.lat,
        nw_lng: northWestBound.lng,
        se_lat: southEastBound.lat,
        se_lng: southEastBound.lng,
        sf: getScalingFactor(map.getZoom(), map.getMaxZoom())
    };

    return queries;
}

// used to scale a LatLngBounds object to 'bufferRatio' percent of 
// its original size. returns LatLngBounds object
// function borrowed from leaflet.js, but with math bugs fixed
function pad(bounds, bufferRatio) {
    var sw = bounds.getSouthWest();
    var ne = bounds.getNorthEast();
    var center = bounds.getCenter();
    var heightBuffer = Math.abs(sw.lat - ne.lat) * bufferRatio;
    var widthBuffer = Math.abs(sw.lng - ne.lng) * bufferRatio;

    return new L.LatLngBounds(
        new L.LatLng(center.lat - heightBuffer*0.5, center.lng - 0.5*widthBuffer),
        new L.LatLng(center.lat + heightBuffer*0.5, center.lng + 0.5*widthBuffer));
}

// gets data scaling factor based on the current zoom level
// returns an int. this number will be interpreted by the server
function getScalingFactor(zoomLevel, maxZoom) {
    return Math.floor(maxZoom/zoomLevel);
}
