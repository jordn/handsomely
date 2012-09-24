		
			var names = new Array();
			var phones = new Array();
			var addresses = new Array();

			function initializeme(city, isLoggedIn) {
				window.LoggedInStatus = isLoggedIn
				jQuery.get("../get_salons?city="+city, function(data){
				//give these arguments, return Jason object
				var dat = JSON.parse(data);
				if (dat.length > 0) {
					//document.getElementById("salon_list").innerHTML="";
					var result_output = "<b>Salons:</b>";
					var salon_list = "<br><ul>";
					var salon_prices = "<br><ul>";
					var salon_addresses = "<br><ul>";
					for (var i = 0; i < dat.length; i++) {
						salon_list += "<li>" + (dat[i].fields.salonName) + "<\/li><br>";
						salon_prices += "<li>" + (dat[i].fields.phone) + "<\/li><br>";
						salon_addresses += "<li>" + (dat[i].fields.address) + "<\/li><br>";
						names[i] = (dat[i].fields.salonName);
						phones[i] = (dat[i].fields.phone);
						addresses[i] = (dat[i].fields.address);
					 }
					//if (isLoggedIn == "true") {
					//	salon_list += "<\/ul><input type=\"submit\" value=\"Go!\" name=\"submit\"></form>";
					//} else {
					//	salon_list += "\/ul><p><b>Please log in or <a href=\"../register\">register</a></b></p></form>";
					//}
					 //document.getElementById("salon_list").innerHTML=result_output + salon_list;
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
		       			position: codeAddress(addresses[i], i, isLoggedIn),	//(locations[i][1], i),
		        		map: map
		      		});
				}
				}); 
			};


			/*  function login(showhide){
			    if(showhide == "show"){
			        document.getElementById('popupbox').style.visibility="visible";
			    }else if(showhide == "hide"){
			        document.getElementById('popupbox').style.visibility="hidden"; 
			    }
			  }*/



			function tellUsers(){
				if (LoggedInStatus == true){
					alert("We will let you know if times are free!");	
  				}
  				else{
  					login("show");
  					/*var r=confirm("You are not logged in. Please click okay to go to the login page or cancel to register.");
					if (r==true){
  						document.location = "http://handsome.ly/login/";
  					}
					else{
  						document.location = "http://handsome.ly/register/";
  					}*/
  				}
			}

			 
			function codeAddress(address, index, isLoggedIn) {
				var geocoder = new google.maps.Geocoder();  
			  	geocoder.geocode( { 'address': address}, function(results, status) {
			   		if (status == google.maps.GeocoderStatus.OK) {
			      		map.setCenter(results[0].geometry.location);
			      		var marker = new google.maps.Marker({
			          		map: map,
			          		position: results[0].geometry.location
			      		});
						var infowindow = new InfoBox();
						google.maps.event.addListener(marker, 'click', (function(marker, index) {
		        			return function() {
								var marker_content = names[index] // phones[index];
								marker_content += "<br>" + phones[index]; //"<br>Price: &pound"; 
								marker_content += "<br><input type = \"button\" onClick=\"tellUsers()\" value = \"Let me know!\">";
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
		      		} 
		      		else {
		        		alert("Geocode was not successful for the following reason: " + status);
		      		}
		    	});
		  	}

