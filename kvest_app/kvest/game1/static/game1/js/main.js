var answer = {selfie:'', place:''};


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function send_answer(){
	if(answer.selfie && answer.place){
		var json_data = JSON.stringify({Answers:answer});
	$.ajax({
			type: "POST",
			url:'/post_answer',
			data:json_data,
			contentType: "application/json; charset=utf-8",
			data_type: 'json',
			
			success: function(data){
				if(data == "True"){
                    $.ajax({
                        type: "GET",
                        url:'/check_answer',
                        success: function(data){
                            if(data=="True"){
                                location.reload()
                            }
                            else{
                                location.reload()
                            }
                        }
                    });
				}else{
					
					location.reload();
				}
			}
		});
	}else{
		document.getElementById("error").innerText = "Take a photos!";
	}
	
}


function take_selfie(){
		// take snapshot and get image data
		 Webcam.freeze( function(data_uri) {
		  // display results in page
		  	document.getElementById('selfie_camera').innerHTML = 
		 	'<img src="'+data_uri+'"/>';
		  	} 
		  );
	}

function take_place(){
	Webcam.freeze(function(data_uri){
			document.getElementById('place_camera').innerHTML = 
			'<img src="'+data_uri+'"/>';
		}
	);
}

function selfie_reset()
{
	$("#exampleModalCenter").modal("hide");
	Webcam.snap(function(data_uri){
		answer.selfie = data_uri;
	});
	Webcam.reset();
	document.getElementById('selfie_btn').innerHTML='OK Make selfie';
}

function place_reset()
{
	$("#placeModalCenter").modal("hide");
	Webcam.snap(function(data_uri){
		answer.place = data_uri;
	});
	Webcam.reset();
	document.getElementById('place_btn').innerHTML = 'OK Make place photo';
}

function delete_photos(){
	if(answer.selfie){
		answer.selfie = "";
		document.getElementById('selfie_btn').innerHTML = 'Make selfie';
	}
	if(answer.place){
		answer.place = "";
		document.getElementById('place_btn').innerHTML = 'Make place photo';
	}
	
}

$('#selfie_btn').on('click', function(){
	$('#exampleModalCenter').modal();
	Webcam.set({
		width:470,
		height:240,
	});
	Webcam.attach('#selfie_camera');
});

$('#exampleModalCenter').on('hidden.bs.modal', function(){
	Webcam.reset()
});

$("#place_btn").on('click', function(){
	$('#placeModalCenter').modal();
	Webcam.set({
		width:470,
		height:240,
	});
	Webcam.attach("#place_camera")
});

$('#placeModalCenter').on('hidden.bs.modal', function(){
	Webcam.reset()
});
