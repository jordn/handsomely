  function login(showhide){
    if(showhide == "show"){
        document.getElementById('popupbox').style.visibility="visible";
    }else if(showhide == "hide"){
        document.getElementById('popupbox').style.visibility="hidden"; 
    }
  }
  
  function ajax_login(showhide){
    if(showhide == "show"){
        document.getElementById('popupbox3').style.visibility="visible";
    }else if(showhide == "hide"){
        document.getElementById('ajax_tellUser').style.visibility="hidden";
        document.getElementById('popupbox3').style.visibility="hidden"; 
    }
  }

  function login2(showhide){
    if(showhide == "show"){
        document.getElementById('popupbox2').style.visibility="visible";
    }else if(showhide == "hide"){
        document.getElementById('popupbox2').style.visibility="hidden"; 
    }
  }

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

  function doAjaxLogin(){
    var pass = document.getElementById('password_ajaxLogin').value; 
    var mail = document.getElementById('email_ajaxLogin').value; 
    var csrftoken = getCookie('csrftoken'); 
    jQuery.post('/ajax_user_login/', {email : mail, password: pass, csrfmiddlewaretoken : csrftoken}, function(data){ djangoUserID = data; }); 
    LoggedInStatus = true; 
    document.getElementById('ajax_tellUser').style.visibility="visible";
  }
  
  function ajax_tellU(salID){
  	tellUsers(salID);
  	document.getElementById('ajax_tellUser').style.visibility="hidden";
  	document.getElementById('popupbox3').style.visibility="hidden"; 
  }
