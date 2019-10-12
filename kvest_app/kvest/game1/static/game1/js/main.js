var answer = {selfie:'', place:''};

// CSRF TOKEN
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

// END 


function readURL(input, item){
	console.log("a");
	if(input.files && input.files[0]){

		var reader = new FileReader();
		reader.onload = function(e){
			if(item == 'selfie')
				answer.selfie = e.target.result;
			if(item == 'place')
				answer.place = e.target.result;
			console.log(answer);
		}
		reader.readAsDataURL(input.files[0]);
	}
}


$('#selfie').change(function(){
	readURL(this, 'selfie');
});

$('#place').change(function(){
	readURL(this, 'place');
});

function get_answer(data){
	$.ajax({
		type: "POST",
		url: 'increment_progress',
		data: JSON.stringify({answer_id: data.id}),
		contentType:"application/json; charset=utf-8",
		data_type: 'json',
		success: function(response_3){
			// May be show some message before

			var data_3 = response_3[0];
			if(data_3.state=="Success"){
				$('#exampleModalCenter').modal('show');
				$('#exampleModalCenter').on('shown.bs.modal', function(e){
					document.getElementById('modal-body').innerHTML = "Ключ: lalala";
				});
				$('#exampleModalCenter').on('hidden.bs.modal', function(e){
					location.reload();
				});
			}else if(data_3.state=="Failed"){
				$('#exampleModalCenter').modal('show');
				$('#exampleModalCenter').on('shown.bs.modal', function(e){
					document.getElementById('modal-body').innerHTML = data_3.msg;
				});
				$('#exampleModalCenter').on('hidden.bs.modal', function(e){
					location.reload();
				});
			}
			
									
		}
	});
}

function disable_all(){
			var selfie = document.getElementById('selfie').setAttribute('disabled', 'disabled');
			var place = document.getElementById('place').setAttribute('disabled', 'disabled');
			var get = document.getElementById('get_mission').setAttribute('disabled', 'disabled');
			var reset = document.getElementById('reset_btn').setAttribute('disabled', 'disabled');
		}


$('#get_mission').on('click', function(){
	disable_all();
	document.getElementById('msg').innerHTML="Ожидайте!";
	if(answer.selfie && answer.place)
	{
		var data = JSON.stringify({Answers:answer});
		$.ajax({
			type: "POST",
			url: "post_answer",
			data: data,
			contentType: "application/json; charset=utf-8",
			data_type: 'json',
			success: function(response){
				console.log(response[0]);
				var data = response[0];
				if(data.state=="Success")
				{
					console.log('1')
					var checkAnswer = setInterval(function(){
						$.ajax({
							type:"POST",
							url: "check_answer",
							data: JSON.stringify({answer_id: data.id}),
							contentType: "application/json; charset=utf-8",
							data_type: 'json',
							success: function(response_2){
								var data_2 = response_2[0];
								if(data_2.state==true){
									clearInterval(checkAnswer);
									get_answer(data);
								}
								else if(data_2.state==false){
									clearInterval(checkAnswer);
									get_answer(data);

								}
								else if(data_2.state==null){

								}
							}
						});
					}, 3000);

					
				}
				else{
					document.getElementById('error').innerHtml="Что-то пошло не так, попробуйте перезагрузить страницу!";
				}
			}

		});
	}
	else{
		document.getElementById('error').style.display = "block";
	}

});





