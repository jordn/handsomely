var locations = [
      ["Lui's",'5a Pembroke Street, Cambridge CB2 3QY', 14],
      ["Mr. Polito's", '4 Silver Street, Cambridge, CB3 9EL, UK', 14],
	  ['Matthew Luke', '53 Trumpington Street Cambridge CB2 1RG', 15.50]
    ];


	var geocoder;
	var logged_in

	logged_in = True


	function initialize() {
	  geocoder = new google.maps.Geocoder();
	  var latlng = new google.maps.LatLng(-34.397, 150.644);
	  var mapOptions = {
  
	    zoom: 17,
	    center: latlng,
	    mapTypeId: google.maps.MapTypeId.ROADMAP
  
	  }
  
	  map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
 
	
		var infowindow = new google.maps.InfoWindow();
		var marker, i;

		for(i=0; i<locations.length; i++){
		
		marker = new google.maps.Marker({
       position: codeAddress(locations[i][1], i),
        map: map
      });
		}
		};




	function myFunction(){

			//if (logged_in == True){
			alert("We will let you know if times are free!");	//}

			//else{alert("Please log in or create an account first!");}
		}
	 
	function codeAddress(address, index) {  
	  geocoder.geocode( { 'address': address}, function(results, status) {
	    if (status == google.maps.GeocoderStatus.OK) {
	      map.setCenter(results[0].geometry.location);
	      var marker = new google.maps.Marker({
	          map: map,
	          position: results[0].geometry.location
	      });
				
				var infowindow = new InfoBox();


			google.maps.event.addListener(marker, 'click', (function(marker, index) {
        	
        	//if (openedInfoWindow != null)
            //	openedInfoWindow.close();

        	return function() {


        		//infowindow.setOptions(myboxOptions);
					
          		//infowindow.open(map, marker);

          		//openedInfoWindow = infowindow;

					var marker_content = locations[index][0];
					marker_content += "<br>Price: &pound" + locations[index][2];
					marker_content += "<br><input type = \"button\" onClick=\"myFunction()\" value = \"Let me know!\">"

					
				var myboxOptions = {
                 content: marker_content 
                ,disableAutoPan: false
                ,maxWidth: 1000

                ,pixelOffset: new google.maps.Size(-60, -110)
                ,zIndex: null
				,shadowStyle: 1
                ,boxStyle: { 
                  	background: "url('tipbox.gif') no-repeat"
                  	,border: "1px solid black"
					,backgroundColor: 'rgb(255,255,255)'
					,opacity: 1
                  	,width: "120px"
                  	,textAlign: "center"
                  	,borderRadius: "10px"				
                 }

                ,closeBoxMargin: "10px 2px 2px 2px"
                ,closeBoxURL: "http://www.google.com/intl/en_us/mapfiles/close.gif"
                ,infoBoxClearance: new google.maps.Size(1, 1)
                ,isHidden: false
                ,pane: "floatPane"
                ,enableEventPropagation: false
        };
				infowindow.setOptions(myboxOptions);
					
          		infowindow.open(map, marker);
					
        }
      })(marker, index));
				
				
				
				
      } else {
        alert("Geocode was not successful for the following reason: " + status);
      }
    });
  }
