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
				$('#deleteBn').removeAttr('disabled');
			}
		});
	});

	// call to delete crawler
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

	// testing iframe
	$('#fakeForm').submit(function(event){
		// cancels the form submission
		event.preventDefault();
		$('#iframe').attr('src',$('#url').val());
	});

	$('#backBn').click(function(event) {
		$.get("/fetch", function( data ) {
			alert( data );
		});
	});

	
	// add more fields
	$('#addBn').click(function(event){
		$('#template').append('<div class="row">' + 
				'Field: <input class="field" type="text" value="" size="10" placeholder="e.g. MySpider">  ' +
				'XPath: <input class="xpath" type="text" size="40" placeholder="e.g. MySpider">' +
				'<br/><br/></div>'
		);
	});

	// add crawler template into form before submit crawler
	$('#create').submit(function( event ) {
		var crawlerTemplate = []
		$(".row").each(function(){
			if ($(this).find('.field').val() != "" || $(this).find('.xpath').val() != "") {
				crawlerTemplate.push('"' + $(this).find('.field').val() + '":"' + $(this).find('.xpath').val() + '"');
			}
		});
		$('#crawlerTemplate').val('{' + crawlerTemplate.toString() + '}');
	});

	$('#monitorLink').click(function(){
		  $('#dataDiv').hide();
		  $('#settingsDiv').hide();
		  $('#monitorDiv').show();
	});
	$('#dataLink').click(function(){
		  $('#monitorDiv').hide();
		  $('#settingsDiv').hide();
		  $('#dataDiv').show();
	});
	$('#settingsLink').click(function(){
		  $('#monitorDiv').hide();
		  $('#dataDiv').hide();
		  $('#settingsDiv').show();
	});
	
	
});
