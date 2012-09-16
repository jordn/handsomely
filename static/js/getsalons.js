function getSalons(city, isLoggedIn) {
	  //this is ajax
	  $.get("../get_salons?city="+city, function(data){
		//give these arguments, return Jason objcect
		var dat = JSON.parse(data);
		if (dat.length > 0) {
			document.getElementById("errors").innerHTML="";
			var result_output = "<b>Salons:</b>";
			var salon_list = "<br><ul>";
			for (var i = 0; i < dat.length; i++) {
			//calculate probability as requested price/salon price
				salon_list += "<li>" + (dat[i].fields.salonName) + "<\/li><br>";
			 }
			if (isLoggedIn == "true") {
				salon_list += "\"><input type=\"submit\" value=\"Go!\" name=\"submit\"></form>";
			} else {
				salon_list += "\"><p><b>Please log in or <a href=\"../register\">register</a></b></p></form>";
			}
			 document.getElementById("salon_list").innerHTML=result_output + salon_list;
		} else {
			document.getElementById("salon_list").innerHTML="";
			document.getElementById("errors").innerHTML="<b>No salons found</b>";
		}
	   }); 
}

