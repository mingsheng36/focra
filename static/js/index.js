$(document).ready(function() {
	
	$('#signin').click(function(event) {

		$.ajax({
			url : '/',
			type: 'POST',
			data : {
				csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
				'username': $('#username').val(),
				'password': $('#password').val()
			},
			success: function( data ){
				if (data == "doesNotExist") {
					alert('Your dont have account with us');
				} else if (data == "success") {
					window.location.href = "/" + $('#username').val();
				}
			}
		});
		
	});
	
	$('#register').click(function(event) {
		$.ajax({
			url : '/register',
			type: 'POST',
			data : {
				csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
				'username': $('#register_username').val(),
				'password': $('#register_password').val()
			},
			success: function( data ){
				if (data == "success") {
					window.location.href = "/" + $('#register_username').val();
				} else if (data == "alreadyExist") {
					alert('Username already taken!');
				} else if (data == 'specialChar') {
					alert('Username should consist of letters and numbers only');
				} else if (data == 'usernameLength') {
					alert('Username should be less than 20 characters');
				} else if (data == 'passwordLength') {
					alert('password should be at least 8 characters');
				}
			}
		});
	});
	
	$(document).keypress(function(e) {
	    if(e.which == 13) {
	    	if ($('#signinDiv').attr('style') != 'display: none;') {
	    		$('#signin').trigger('click');
	    	}
	    	else if ($('#registerDiv').attr('style') != 'display: none;') {
	    		$('#register').trigger('click');
	    	}
	    }
	});
	
	$('.links').click(function(event){
		var name = $(this).attr('id');
		if (name == 'signinLink') {
			$('#signinLink').addClass('active');
			$('#registerLink').removeClass('active');
			$('#contactLink').removeClass('active');
			$('#registerDiv').hide();
			$('#contactDiv').hide();
			$('#signinDiv').fadeIn('fast');
		} else if (name == 'registerLink') {
			$('#signinLink').removeClass('active');
			$('#registerLink').addClass('active');
			$('#contactLink').removeClass('active');
			$('#registerLink').addClass('active');
			$('#signinDiv').hide();
			$('#registerDiv').fadeIn('fast');
			$('#contactDiv').hide();
		} else if (name == 'contactLink') {
			$('#signinLink').removeClass('active');
			$('#registerLink').removeClass('active');
			$('#contactLink').addClass('active');
			$('#contactLink').addClass('active');
			$('#signinDiv').hide();
			$('#registerDiv').hide();
			$('#contactDiv').fadeIn('fast');
		}
	});
	
});