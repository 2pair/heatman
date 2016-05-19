"use strict";

// singleton for handling rest functionality
function Rest() {
    // ------- begin singleton code -------
    // cached instance
    var instance; 
    Rest = function Rest() {
        return instance;
    };
    Rest.prototype = this;
    instance = new Rest();
    instance.constructor = Rest;
    // -------- end singleton code --------
    
    // objects for constructing URI
    instance.queries = [];
    instance.address = window.location.href.split('?')[0];
    
    // return the current queries object
    this.getQueries = function() {
        return instance.queries;
    };
    
    // sets our queries object equal to the queries object passed in
    this.setQueries = function(q) {
        instance.queries = q;
    };

    // creates the URI to be used for the rest call
    // returns a string consisting of the address and queries
    this.constructURI = function() {
        var keys = [];
        for (var k in instance.queries) keys.push(k);
     
        var uri = instance.address + '?';
      
        for (var i = 0; i < keys.length; i++) {
            uri += keys[i] + '=' + instance.queries[keys[i]];
            if (i < (keys.length - 1)){
                uri += '&';
            }
        }
        
        return uri;
    };
    
    // sends a new REST Request
    // passes the return value to some callback, as well as an array of args
    this.sendReceive = function(uri, callback, cbthis, cbargs) {
        var xhttp = new XMLHttpRequest();
        
        // add xhttp as the first object in the args array
        for (var i = cbargs.length; i >= 0; i--) {
            cbargs[i] = cbargs[i - 1];
        }
        cbargs[0] = xhttp;
        
        xhttp.onreadystatechange = function() {
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                callback.apply(cbthis, cbargs);
            }
        };
        
        xhttp.open('GET',uri,true);
        xhttp.send();
    };
}
