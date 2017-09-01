var appClient

       
/*************************************************************************************************
                       GARBAGE BIN MOBILE APP
**************************************************************************************************/
var app = {
/*************************************************************************************************
    FUNCTION NAME : initialize()
    DESCRIPTION   : initialize the app with events
**************************************************************************************************/
    initialize: function() {
        this.bindEvents();
        $(window).on("navigate", function (event, data) {          
            event.preventDefault();      
        })
    },
/**************************************************************************************************
    FUNCTION NAME : bindEvents()
    DESCRIPTION   : Initialize Pubnub and adds device ready eventListner to app 
****************************************************************************************************/ 
    bindEvents: function() {
       /*Syntax: document.addEventListener(event, function, useCapture)
        event : A String that specifies the name of the event.
        function :  Specifies the function to run when the event occurs.
        useCapture :  A Boolean value that specifies whether the event should be executed in the capturing or in the bubbling phase. 
             true - The event handler is executed in the capturing phase
             false- Default. The event handler is executed in the bubbling phase */
 
        document.addEventListener('deviceready', this.onDeviceReady, false);
        app.mqttInit();
    },
/**************************************************************************************************
    FUNCTION NAME : onDeviceReady()
    DESCRIPTION   : pass device ready id to received event 
****************************************************************************************************/   
    onDeviceReady: function() {
        app.receivedEvent('deviceready');
        console.log('deviceready');
         
    },
/**************************************************************************************************
    FUNCTION NAME : receivedEvent()
    DESCRIPTION   : on Deviceready loads the app displaying main page
****************************************************************************************************/ 
    receivedEvent: function(id) {
        var parentElement = document.getElementById(id);
        console.log(parentElement);
        // Returns the first Element within the document that matches the specified selector, or group of selectors
        var listeningElement = parentElement.querySelector('.listening');
        console.log(listeningElement);
        var receivedElement = parentElement.querySelector('.received');
        console.log(receivedElement);
        listeningElement.setAttribute('style', 'display:none;');
        receivedElement.setAttribute('style', 'display:block;');
    },
/**************************************************************************************************
    FUNCTION NAME : mqttInit()
    DESCRIPTION   : initialize pubnub keys and set app to default function 
****************************************************************************************************/ 
    mqttInit: function() {

        
        var Client = require('ibmiotf');
        var appClientConfig = {
        "org" : "o15j1s",
        "id" : "HELLO_IOT_APP_001",
        "domain": "internetofthings.ibmcloud.com",
        "type" : "IOTIFY_APP",
        "auth-method" : "apikey",
        "auth-key": "a-o15j1s-wwlr9tbpwp",
        "auth-token" : "87+21Y8OxG(2uHbdIX"
        };
      appClient = new Client.IotfApplication(appClientConfig);
      
      appClient.connect();
       
       console.log('connected');
        appClient.on('connect', function () {
            
            appClient.subscribeToDeviceEvents("raspberry_pi");
            app.subscribe();

             
    	});
        
        
     

        
    },
/**************************************************************************************************
    FUNCTION NAME : sensordisplay()
    DESCRIPTION   : displays temperature and humidity levels
****************************************************************************************************/ 
    sensordisplay:function(Air_temperature, humidity, soil_moisture, soil_temperature) {
        $temp = $("#temp001");
        $humid = $("#humid001");
        $soil_moisture = $("#soilMois001");
        $soil_temp = $("#soilTemp001");
       // $temp[0].innerText = '' + temperature.toFixed(2) + '°C';
       // $humid[0].innerText = '' + humidity.toFixed(2) + '%';
    },



    subscribe: function(){  
    	console.log('subscribing');
        appClient.on("deviceEvent", function (deviceType, deviceId, eventType, format, payload) {
        console.log('got a message');
        console.log("Device Event from :: "+deviceType+" : "+deviceId+" of event "+eventType+" with payload : "+payload);
        var parsed = JSON.parse(payload);
        console.log(parsed.Air_temperature, parsed.humidity, parsed.soil_moisture, parsed.soil_temperature); 
        
        app.sensordisplay(parsed.Air_temperature, parsed.humidity, parsed.soil_moisture, parsed.soil_temperature);
         
        
    });

     }
};
