      var geocoder;
      var map;
      function initialize(address) {
        geocoder = new google.maps.Geocoder();
        var latlng = new google.maps.LatLng(52.205277,0.121945);
        var mapOptions = {
          	zoom: 17,
			minZoom: 10,
			maxZoom: 20,
			center: latlng,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        }
        var markerPosition = codeAddress(address);
        map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
        var styles = [
			  {
			    stylers: [
			      { hue: "#336600" },
			      { saturation: 0 },
			      { invert_lightness: true }
			    ]
			  },{
			    featureType: "road",
			    elementType: "geometry",
			    stylers: [
			      { lightness: 10 },
			      { visibility: "simplified" }
			    ]
			  },{
			    featureType: "road",
			    elementType: "labels",
			    stylers: [
			      { visibility: "off" }
			    ]
			  }
			];

		map.setOptions({styles: styles});
      }

      function codeAddress(address) {
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode( { 'address': address}, function(results, status) {
          if (status == google.maps.GeocoderStatus.OK) {
            map.setCenter(results[0].geometry.location);
            var marker = new google.maps.Marker({
                map: map,
                position: results[0].geometry.location
            });
            marker.setIcon('http://labs.google.com/ridefinder/images/mm_20_orange.png')

          } else {
            alert('Geocode was not successful for the following reason: ' + status);
          }
        });
      }