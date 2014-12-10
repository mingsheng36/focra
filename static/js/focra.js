$(document).ready(function() {
	$("#start").click( function(event) {
		$('#display').html('Initializing..');
		$.get('/start/', function(data){
			$('#display').html(data);
		});
	});

	$("#stop").click( function(event) {
		$('#display').html('Terminating..');
		$.get('/stop/', function(data){
			$('#display').html(data);
		});
	});
});

