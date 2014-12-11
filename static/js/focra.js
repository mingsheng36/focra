$(document).ready(function() {
	// call to start crawler
	$('#startBn').click(function(event) {
		$('#display').html('Initializing..');
	});
	
	// call to stop crawler
	$('#stopBn').click( function(event) {
		$('#display').html('Terminating..');
		$.get('/stop/', function(data){
			$('#display').html(data);
		});
	});
	
	// show and hide div
	$('a[href="#createCrawler"]').click(function(){
		$("#createDiv").fadeIn("fast", "linear");
	});
	
});

//$.ajax({
//    url : /start/,
//    type: 'POST',
//    data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
//    		crawlerName : $('#crawlerName').val(), 
//    		crawlerSeeds : $('#crawlerSeeds').val()},
//    success: function( data ){
//    	$('#display').html(data);
//    	$("#createDiv").hide();
//    }
//});