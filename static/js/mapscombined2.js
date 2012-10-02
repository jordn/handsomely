		
			var names = new Array();
			var phones = new Array();
			var addresses = new Array();
			var cut = new Array();
			var prices = new Array();
			var mon = new Array();
			var tue = new Array();
			var wed = new Array();
			var thu = new Array();
			var fri = new Array();
			var sat = new Array();
			var sund = new Array();

//this extracts the data from the PriceMenu model and is called from the initializeme loop
			function parsePrice(key, index){
				jQuery.get("../get_salons_price_menu?salonID=" + key, function(data){
				dat_price = JSON.parse(data);
				return prices[index] = dat_price[index].fields.servicePrice, cut[index] = dat_price[index].fields.serviceName
				});
			}


			function parseHours(key, index){
				jQuery.get("../get_salons_opening_hours?salonID=" + key, function(data){
				dat_hours = JSON.parse(data);
				k = 0
					while (k<7){		
						if ((dat_hours[k].fields.dayOfTheWeek = "MON") && (dat_hours[k].fields.salonID = key)){
								mon[index]= [dat_hours[k].fields.openingTime, dat_hours[k].fields.closingTime]
								k = k+1
							
						}
						if ((dat_hours[k].fields.dayOfTheWeek = "TUE") && (dat_hours[k].fields.salonID = key)){
							tue[index]=[dat_hours[k].fields.openingTime, dat_hours[k].fields.closingTime]
							k = k+1
						
						}
						if ((dat_hours[k].fields.dayOfTheWeek = "WED") && (dat_hours[k].fields.salonID = key)){
							wed[index] = [dat_hours[k].fields.openingTime, dat_hours[k].fields.closingTime]
							k = k+1
						
						}
						if ((dat_hours[k].fields.dayOfTheWeek = "THU") && (dat_hours[k].fields.salonID = key)){
							thu[index] = [dat_hours[k].fields.openingTime, dat_hours[k].fields.closingTime]
							k = k+1
						
						}
						if ((dat_hours[k].fields.dayOfTheWeek = "FRI") && (dat_hours[k].fields.salonID = key)){
							fri[index] = [dat_hours[k].fields.openingTime, dat_hours[k].fields.closingTime]
							k = k+1
						
						}
						if ((dat_hours[k].fields.dayOfTheWeek = "SAT") && (dat_hours[k].fields.salonID = key)){
							sat[index] = [dat_hours[k].fields.openingTime, dat_hours[k].fields.closingTime]
							k = k+1
						
						}
						if ((dat_hours[k].fields.dayOfTheWeek = "SUN") && (dat_hours[k].fields.salonID = key)){
								sund[index] = [dat_hours[k].fields.openingTime, dat_hours[k].fields.closingTime]	
								k = k+1
						}

					}
				return mon, tue, wed, thu, fri, sat, sund;
				});
			}




			function initializeme(city, isLoggedIn, djangoUserID) {
				window.LoggedInStatus = isLoggedIn
				window.djangoUserID = djangoUserID
				jQuery.get("../get_salons?city="+city, function(data){
				//give these arguments, return Jason object
				var dat = JSON.parse(data);
				if (dat.length > 0) {
					//document.getElementById("salon_list").innerHTML="";
					var result_output = "<b>Salons:</b>";
					var salon_list = "<br><ul>";
					var salon_prices = "<br><ul>";
					var salon_addresses = "<br><ul>";
					var dat_price
					for (var i = 0; i < dat.length; i++) {
						salon_list += "<li>" + (dat[i].fields.salonName) + "<\/li><br>";
						salon_prices += "<li>" + (dat[i].fields.phone) + "<\/li><br>";
						salon_addresses += "<li>" + (dat[i].fields.address) + "<\/li><br>";
						names[i] = (dat[i].fields.salonName);
						phones[i] = (dat[i].fields.phone);
						addresses[i] = (dat[i].fields.address);
						parsePrice(dat[i].pk, i)		//taking the primary key, but this is not compatible with the salonID.
						parseHours(dat[i].pk, i)
					}
				} 
				else {
					document.getElementById("salon_list").innerHTML="";
					document.getElementById("salon_list").innerHTML="<b>No salons found</b>";
				}
			  	var geocoder = new google.maps.Geocoder();
			  	var latlng = new google.maps.LatLng(52.205, 0.175);
			  	var mapOptions = {
		  			zoom: 16,
			    	center: latlng,
			    	mapTypeId: google.maps.MapTypeId.ROADMAP
			  		}
			  	map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
				for(var i = 0; i < names.length; i++){
					var marker = new google.maps.Marker({
		       			position: codeAddress(addresses[i], i, dat[i].pk),
		        		map: map
		      		});
				}
				});
			};

			function tellUsers(salonID){
				if (LoggedInStatus == true){
					if (djangoUserID != -1) {
                        document.getElementById('getNotifiedButton').innerHTML = "Loading..."; 
						jQuery.get("/create_notification_request/?salonID=" + salonID + "&djangoUserID=" + djangoUserID, function(data){ alert("We will let you know if times are free!");
						});
                        document.getElementById('getNotifiedButton').innerHTML = "Done!"; 
					}		
  				}
  				else{
  					login("show");
  				}
			}
			 
			function codeAddress(address, index, salonID) {
				var geocoder = new google.maps.Geocoder();  
			  	geocoder.geocode( { 'address': address}, function(results, status) {
			   		if (status == google.maps.GeocoderStatus.OK) {
			      		map.setCenter(results[0].geometry.location);
			      		var marker = new google.maps.Marker({
			          		map: map,
			          		position: results[0].geometry.location
			      		});

						//This code does the infoboxes
						var infowindow = new InfoBox();
						google.maps.event.addListener(marker, 'click', (function(marker, index) {
		        			return function() {
								var marker_content = names[index];
								marker_content += "<br>" + cut[index] + ": &pound" + prices[index]; 
								marker_content += "<br>" + phones[index];

								if (mon[index][0] == mon[index][1]){
									marker_content += "<br>" + "Monday: CLOSED "
								}
								else{
									marker_content += "<br>" + "Monday: " + mon[index][0] + "-" + mon[index][1];
								}

								if (tue[index][0] == tue[index][1]){
									marker_content += "<br>" + "Tuesday: CLOSED "
								}
								else{
								marker_content += "<br>" + "Tuesday: " + tue[index][0] + "-" + tue[index][1];
								}

								if (wed[index][0] == wed[index][1]){
									marker_content += "<br>" + "Wednesday: CLOSED "
								}
								else{
									marker_content += "<br>" + "Wednesday: " + wed[index][0] + "-" + wed[index][1];
								}

								if (thu[index][0] == thu[index][1]){
									marker_content += "<br>" + "Thursday: CLOSED "
								}
								else{
									marker_content += "<br>" + "Thursday: " + thu[index][0] + "-" + thu[index][1];
								}

								if (fri[index][0] == fri[index][1]){
									marker_content += "<br>" + "Friday: CLOSED "
								}
								else{
									marker_content += "<br>" + "Friday: " + fri[index][0] + "-" + fri[index][1];
								}

								if (sat[index][0] == sat[index][1]){
									marker_content += "<br>" + "Saturday: CLOSED "
								}
								else{
									marker_content += "<br>" + "Saturday: " + sat[index][0] + "-" + sat[index][1];
								}

								if (sund[index][0] == sund[index][1]){
									marker_content += "<br>" + "Sunday: CLOSED "
								}
								else{
									marker_content += "<br>" + "Sunday: " + sund[index][0] + "-" + sund[index][1];
								}

								//marker_content += "<br><input type = \"button\" onClick=\"tellUsers(" + salonID + ")\" value = \"Email me when they are free!\">";
								marker_content += "<br><input type = \"button\" onClick=\"tellUsers(" + salonID + ")\" id=\"getNotifiedButton\" value = \"Email me when they are free!\">"; 
								var myboxOptions = {
		                 			content: marker_content 
					                ,disableAutoPan: false
					                ,maxWidth: 1000
					                ,pixelOffset: new google.maps.Size(-100, -110)
					                ,zIndex: null
									,shadowStyle: 1
					                ,boxStyle: { 
					                  	background: "url('tipbox.gif') no-repeat"
					                  	,border: "1px solid black"

										,backgroundColor: 'rgb(255,255,255)'
										,opacity: 1
					                  	,width: "200px"
					                  	,textAlign: "center"
					                  	,borderRadius: "10px"				
		                 			}
					                ,closeBoxMargin: "2px 2px 2px 2px"
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


		      		} 
		      		else {
		        		alert("Geocode was not successful for the following reason: " + status);
		      		}
		    	});
		  	}

