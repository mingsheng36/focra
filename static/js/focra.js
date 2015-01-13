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

	// step 1 (fetch url)
	if ($('#url').val() != "") {
		$('#step_one_instruction').hide();
		$('#step_one_bn').fadeIn('fast');
	}
	
	$('#url').on('input propertychange', function(event) {
		if ($('#url').val() != "") {
			$('#step_one_instruction').fadeOut('fast', function(event){
				$('#step_one_bn').fadeIn('fast');
			});
			
		} else {
			$('#step_one_bn').fadeOut('fast', function(event) {
				$('#step_one_instruction').fadeIn('fast');	
			});
		}
	});

	$('#step_one_bn').click(function(event) {
		$('#step_one_bn').fadeOut('fast', function(event){
			$('#loader').fadeIn('fast');
		});
		$.ajax({
			url: "/fetch",
			data: { 
				"url": $('#url').val(), 
			},
			type: "GET",
			success: function(res) {
				$('#iframe').attr('srcdoc', res);
				$('#templates').empty();
				$('#iframe').load(function(){
					$('#loader').fadeOut('fast');
					$('#step_one').fadeOut('fast', function(event){
						$('#step_two').fadeIn('fast');
						$('.field').focus();
					});
				});
			}
		});

	});
	
	// step 2 (select fields)
	var xpath = []
	if($('.field').val() != "") {
		$('#step_two_instruction_1').hide();
		$('#step_two_instruction_2').fadeIn('fast');
	}
	$('.field').on('input propertychange', function(event){
		if ($('.field').val() != "") {
			$('#step_two_instruction_1').fadeOut('fast', function(event){
				$('#step_two_instruction_2').fadeIn('fast');
			});
		} else if($('.field').val() != "" && xpath.length > 0){
			$('#step_two_instruction_2').fadeOut('fast', function(event){
				$('#add_field_bn').fadeOut('fast');
				$('#step_two_bn').fadeOut('fast');
				$('#step_two_instruction_1').fadeIn('fast');
			});
		}
	});
	
	$('#add_field_bn').click(function(event){
		$('.field-div').append('<input class="field form-control" type="text" size="20" size="10" placeholder="Field Name Here">' +
			'<div class="form-control"><span class="badge">0</span></div>');
	});
	
	$('#step_two_bn').click(function(event) {
		var crawlerTemplate = []
		$(".field").each(function(i){
			if ($(this).val() != "" && xpath[i] != "") {
				crawlerTemplate.push('"' + $(this).val() + '":"' + xpath[i] + '"');
			}
		});
		// add crawler template into form
		$('#crawlerTemplate').val('{' + crawlerTemplate.toString() + '}');
		$('#step_two').fadeOut('fast', function(event){
			$("#step_three").fadeIn('fast');
		});
	});
	
	// step 3 (crawler name)
	$('#crawlerName').on('input propertychange', function(event){
		if ($('#crawlerName').val() != "") {
			$('#step_three_bn').fadeIn('fast');
		} else {
			$('#step_three_bn').fadeOut('fast');
		}
	});

	// iframe event handlers for visual selection
	$('#iframe').load(function(){
		var contain_texts;
		$(this.contentWindow.document).mouseover(function (event) {
			contain_texts = $(event.target).clone().children().remove().end().text();
			if ($(event.target).prop("tagName").toLowerCase() == 'img') {
				$('#display').html($(event.target).attr("src").toLowerCase());
				$(event.target).addClass( "outline-element" );
			} 
			else if (contain_texts.trim()) {
				$('#display').html(contain_texts);
				$(event.target).addClass( "outline-element" );
			}
		}).mouseout(function (event) {
			$(event.target).removeClass('outline-element');
		}).click(function (event) {
			if ($(event.target).prop("tagName").toLowerCase() == 'img' || contain_texts.trim()) {
				$(event.target).toggleClass('outline-element-clicked');
				getElementTreeXPath(event.target)
				xpath.push(getElementTreeXPath(event.target));
				getRows();
				if ($('.field').val() != "" && xpath[0] != ""){
					$('#step_two_instruction_2').fadeOut('fast', function(event){
						$('#add_field_bn').fadeIn('fast');
						$('#step_two_bn').fadeIn('fast');
					});
				}
//				alert($('#iframe').contents().xpath(getElementTreeXPathNode(event.target)).html());
//				alert(
//						document.getElementById('iframe').contentWindow.document.evaluate(
//								getElementTreeXPathNode(event.target),
//								document.getElementById('iframe').contentWindow.document,
//								null,
//								XPathResult.FIRST_ORDERED_NODE_TYPE,
//								null).singleNodeValue.textContent
//					);
			}
		});
	});
	
	function getRows() {
		return 1;
	}
	
	// function to get absolute xpath from the iframe DOM object
	function getElementTreeXPath(element) {
		var xpath_length = $(element).parents().andSelf().length;
		return "/" + $(element).parents().andSelf().map(function(i, obj) {
			var $this = $(this);
			var tagName = this.nodeName;
			
			if (tagName.toLowerCase() == 'tbody') {
				return null;
			} else if ($this.siblings(tagName).length > 0) {
				tagName += "[" + ($this.prevAll(tagName).length + 1) + "]";
			}
			if (i == xpath_length-1) {
				if (tagName.toLowerCase() == 'img') {
					tagName = tagName + "/@src";
				} else {
					tagName = tagName + "/text()";
				}
			}
			return tagName;
		}).get().join("/").toLowerCase();
	};
	
	// function to get xpath node from the iframe DOM object
	function getElementTreeXPathNode(element) {
		var xpath_length = $(element).parents().andSelf().length;
		return "/" + $(element).parents().andSelf().map(function(i, obj) {
			var $this = $(this);
			var tagName = this.nodeName;
			
			if ($this.siblings(tagName).length > 0) {
				tagName += "[" + ($this.prevAll(tagName).length + 1) + "]";
			}
			return tagName;
		}).get().join("/").toLowerCase();
	};
		
	// load data section
	var loaded = false;
	var fields = [];
	$(".fields").each(function(){
		fields.push($(this).html());
	});
	
	$('#data_tab').click(function(){
		
		if (!loaded) {
			$.ajax({
				url: "/data",
				type: "GET",
				success: function(res) {
					//empty not loaded
					if (res.length == 2) {
						loaded = false;
					}
					else {
						var data = $.parseJSON(res);
						$.each(data, function(i, obj) {
							var rowData = "";
							for (i = 0; i < fields.length; i++) { 
								rowData = rowData + "<td>" + obj[fields[i]] + "</td>"
							}

							$('#crawlerData').append(
									"<tr>" + rowData + "</tr>"		
							);
						});
						loaded = true;
					}
				}
			});
			
		}
	});
	
	
});
