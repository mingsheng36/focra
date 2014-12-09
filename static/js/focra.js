$(document).ready(function() {
	$("#start").click( function(event) {
		$.get('/start/', function(data){
			$('#display').html(data);
		});
	});

	$("#stop").click( function(event) {
		$.get('/stop/', function(data){
			$('#display').html(data);
		});
	});
});

