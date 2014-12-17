$(document).ready(function() {
	// call to start crawler
	$('#startBn').click(function(event) {
		$('#display').html('Initializing..');
		$('#startBn').attr('disabled','disabled');
		$('#deleteBn').attr('disabled', 'disabled');
		$.ajax({
			url : '/start',
			type: 'POST',
			data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
			success: function( data ){
				$('#display').html(data);
				$('#stopBn').removeAttr('disabled');	    	
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
				$('#stopBn').attr('disabled','disabled');
				$('#startBn').removeAttr('disabled');
				$('#deletBn').removeAttr('disabled');
			}
		});
	});

	$('#deleteBn').click(function(event) {
		var r = confirm("Are you sure you want to delete?")
		if (r == true) {
			$('#display').html('Deleting..');
			$.ajax({
				url : '/delete',
				type: 'POST',
				data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
				success: function( data ){
					$('#display').html(data);
					window.location.href = '/' + $('#username').html()
				}
			});
		} 
	});

	$('#fakeForm').submit(function(event){
		// cancels the form submission
		event.preventDefault();
		$('#iframe').attr('src',$('#url').val());
	});

//	$('#fetchBn').click(function(event) {
//		$.get("/fetch", function( data ) {
//			alert( data );
//		});
//	});
	
});
