$(document).ready(function() {
	// call to start crawler
	$('#startBn').click(function(event) {
		$('#display').html('Initializing..');
		$.ajax({
		    url : '/start',
		    type: 'POST',
		    data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
		    success: function( data ){
		    	$('#display').html(data);
		    }
		});
	});
	
	// call to stop crawler
	$('#stopBn').click( function(event) {
		$('#display').html('Terminating..');
		$.ajax({
		    url : '/stop',
		    type: 'POST',
		    data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
		    success: function( data ){
		    	$('#display').html(data);
		    }
		});
	});
	
});
