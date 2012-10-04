//-----------------Description--------------
//This file accesses the salon database and displays the map with salon details on it


//These are global variables: defined such because they are used in various functions		
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

//-------------------------Javascript origin starts further down-----------------------------------


//this extracts the data from the PriceMenu model and is called from the initializeme loop. Arguments are salon PK (identifier), and index for list.
			function parsePrice(key, index){
				//extracts data in a same way as that done in initializeme from http://handsome.ly/get_salons_price_menu/?salonID=6
				jQuery.get("../get_salons_price_menu?salonID=" + key, function(data){
				//define this data as dat_price
				dat_price = JSON.parse(data);
				//for each data set in dat_price
				for (var a = 0; a < dat_price.length; a++){
					//if the salonID (defined by the user in handsome.ly/admin) is the same as the primary key then 
					if (dat_price[a].fields.salonID == key) {
						//update this element of the price array and the cut array (what type of haircut it is)
						prices[index] = dat_price[a].fields.servicePrice, cut[index] = dat_price[a].fields.serviceName
					}
				}
				});
			}


//called from initializeme  with arguments of salon primary key (basically identifier) and index for lists
			function parseHours(key, index){
				//does same data extraction from eg http://handsome.ly/get_salons_opening_hours/?salonID=6
				jQuery.get("/get_salons_opening_hours?salonID=" + key, function(data){
				//define this data as dat_hours (this is the data for just one salon)
				dat_hours = JSON.parse(data);
				k = 0
					//for each day of the week
					while (k<7){	
						//if the day from this element is monday and the user-defined salonID is the same as the automatically-defined primary key then	
						if ((dat_hours[k].fields.dayOfTheWeek = "MON") && (dat_hours[k].fields.salonID = key)){
							//add to the monday array of opening and closing hours
							mon[index]= [dat_hours[k].fields.openingTime, dat_hours[k].fields.closingTime]
							k = k+1
						//etc............up until sunday. All days of the week must be defined otherwise you will never escape this loop, which is a downside.	
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
						//Note that sunday array is called sund as sun is something else in JS
						if ((dat_hours[k].fields.dayOfTheWeek = "SUN") && (dat_hours[k].fields.salonID = key)){
							sund[index] = [dat_hours[k].fields.openingTime, dat_hours[k].fields.closingTime]	
							k = k+1
						}

					}
				return mon, tue, wed, thu, fri, sat, sund;
				});
			}



//This is where the javascript is first called from the index.html file. Hence the name, initializeme. ;)
//city is, in this instance Cambridge.
			function initialize_map_with_markers(city, isLoggedIn, djangoUserID) {
				window.LoggedInStatus = isLoggedIn		//global variable isLoggedIn
				window.djangoUserID = djangoUserID
				//This uses the data at http://handsome.ly/get_salons/?city=cambridge 
				jQuery.get("/get_salons?city="+city, function(data){
				//This extracts the data in a useful form. Try putting it in http://json.parser.online.fr/ and see what the output is.
				var dat = JSON.parse(data);
				//define this extracted data as dat. If there actually is some data
				if (dat.length > 0) {
					//this is not actually necessary, but will be useful later when we list salons down the LHS
					var result_output = "<b>Salons:</b>";
					var salon_list = "<br><ul>";
					var salon_prices = "<br><ul>";
					var salon_addresses = "<br><ul>";
					//for each salon, extract the name, phone no etc from the parsed data
					for (var i = 0; i < dat.length; i++) {
						names[i] = (dat[i].fields.salonName);
						phones[i] = (dat[i].fields.phone);
						addresses[i] = (dat[i].fields.address);
						//call the function parsePrice with the arguments of salons primary key (identifier) and index
						parsePrice(dat[i].pk, i)
						//call the function parseHours with the arguments of salons primary key (identifier) and index		
						parseHours(dat[i].pk, i)
					}
				} 
				else {
					//If there is nothing there then let them know
					document.getElementById("salon_list").innerHTML="";
					document.getElementById("salon_list").innerHTML="<b>No salons found</b>";
				}
				//GOOGLE CODE
				//taken from google maps API documentation. Need to use the geocoder definition, which converts addressed into lat/long
			  	var geocoder = new google.maps.Geocoder();
			  	var latlng = new google.maps.LatLng(52.205277,0.121945);
			  	var mapOptions = {
					zoom: 15,
					minZoom: 10,
					maxZoom: 20,
			    	center: latlng,
			    	mapTypeId: google.maps.MapTypeId.ROADMAP
			  		}
			  	//create a new map variable and shove it in the map_canvas id element.
			  	map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
			  	//END GOOGLE CODE
			  	var markerPosition;
			  	//if the primary key is more than 17 then call cachedAddress, otherwise call codeAddress. This is because the google maps API only allows geocoding of 
			  	//10 data points. Beyond this, we have to manually input the latitude and longitude in the address field in handsome.ly/admin
			  	//It starts at 17, because our first PK is 6 and not 1.
				for(var i = 0; i < names.length; i++){
					if (dat[i].pk > 17) {
						markerPosition = cachedAddress(dat[i].fields.address, i, dat[i].pk)
					} else {
						markerPosition = codeAddress(addresses[i], i, dat[i].pk)
					}
					//create a marker with the position as extracted from cached or code Address.
					var marker = new google.maps.Marker({
		       			position: markerPosition,
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
  					ajax_login("show");
  					window.Ajax_salonID = salonID;
  					if (djangoUserID != -1) {
						document.getElementById('getNotifiedButton').innerHTML = "Loading..."; 
									jQuery.get("/create_notification_request/?salonID=" + salonID + "&djangoUserID=" + djangoUserID, function(data){ alert("We will let you know if times are free!");
									});
						document.getElementById('getNotifiedButton').innerHTML = "Done!"; 
					}
  				}
			}
			 

			function codeAddress(address, index, salonID) {
				//geocoder needs to be loaded from maps API
				var geocoder = new google.maps.Geocoder(); 
				//geocode the address 
			  	geocoder.geocode( { 'address': address}, function(results, status) {
			   		if (status == google.maps.GeocoderStatus.OK) {
			   			//set the centre of the map in the centre of cambridge
			      		map.setCenter(new google.maps.LatLng(52.206153,0.123022));
			      		var marker = new google.maps.Marker({
			          		map: map,
			          		position: results[0].geometry.location
			      		});

						//This code does the infoboxes. Infobox allows for greater flexibility that infowindow
						var infowindow = new InfoBox();
						//listener is the click.
						google.maps.event.addListener(marker, 'click', (function(marker, index) {
		        			return function() {
		        				//add all the content that has been generated in HTML format
								var marker_content = "<span class='salon_name'>" + names[index] + "</span>";
								marker_content += "<i class='icon-tag'></i><span class='haircut'>" + cut[index] + "</span> <span class='price'>&pound" + prices[index] + "</span>"; 
								marker_content += "<span class='phone_number'>" + phones[index] + "</span>";
								marker_content += "<span class='timetable'>"
								//if the opening and closing hours are the same then it is closed.
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
								marker_content += "</span>" //this is closing the timetable class
								//this is the "let me know" button
								marker_content += "<br><i class='icon-envelope'></i><input type='button' onClick='tellUsers(" + salonID + ")' class='getNotifiedButton btn-block btn-primary' value=\"Notify me when it's quiet\">"; 
								//defined all the infobox parameters.
								var myboxOptions = {
		                 			content: marker_content 
					                ,disableAutoPan: false
					                ,maxWidth: 1000
					                ,pixelOffset: new google.maps.Size(-100, -110)
					                ,zIndex: null
									,shadowStyle: 1
					                ,closeBoxMargin: "2px 2px 2px 2px"
					                ,closeBoxURL: "http://www.google.com/intl/en_us/mapfiles/close.gif"
					                ,infoBoxClearance: new google.maps.Size(1, 1)
					                ,isHidden: false
					                ,pane: "floatPane"
					                ,enableEventPropagation: false
		        				};
		        				//sets the infobox
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