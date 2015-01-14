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

	$('#delete').submit(function(event) {
		var choice = confirm("Are you sure you want to delete?");
		if (choice == false) {
			event.preventDefault();
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
			$('#url').prop('disabled', true);
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
					$('#url').prop('disabled', false);
					$('#step_one').fadeOut('fast', function(event){
						$('#step_two').fadeIn('fast');
						$('.field').focus();
					});
				});
			}
		});

	});
	
	// step 2 (select fields)
	if ($('.field').val() != "") {
		$('#step_two_instruction_1').hide();
		$('#ifb').hide();
		$('#step_two_instruction_2').fadeIn('fast');
	}
	
	// iframe event handlers for visual selection
	var field_xpaths = []
	var refined_xpath = "";
	var sample_xpaths = [];
	var candidate_xpaths = [];
	
	$('#iframe').load(function(){
		var contain_texts;
		$(this.contentWindow.document).mouseover(function (event) {
			contain_texts = $(event.target).clone().children().remove().end().text();
			if ($(event.target).prop("tagName").toLowerCase() == "img") {
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

				sample_xpaths.push(getElementTreeXPath(event.target));
				candidate_xpaths = get_candidate_xpaths(sample_xpaths);
				
				$('.badge').last().html(candidate_xpaths.length);
				
				if ($('.field').val() != "" && field_xpaths[0] != ""){
					$('#step_two_instruction_2').fadeOut('fast', function(event){
						$('#done_bn').fadeIn('fast');
					});
				}
			}
		});
	});
	
	// Simple Tree Matching Algorithm here (returns a list of candidate_xpaths
	function get_candidate_xpaths(sample_xpaths) {
		
		if (sample_xpaths.length == 1) {
			
			
			// always update refined_xpath before returning candidates
			refined_xpath = sample_xpaths[0];
			return sample_xpaths;
			
		} else if (sample_xpaths.length > 1) {
			for (i = 0; i < sample_xpaths.length; i++) {
				
			}
			refined_xpath = sample_xpaths[0];
			return sample_xpaths;
		} else {
			return null;
		}
		
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
	
	// fields input change detector
	$('#fields').on('input propertychange','.field', function(event){
		//alert($(this).val() + $(this).index('.field'));
		if ($(this).val() != "") {
			$('#step_two_instruction_1').fadeOut('fast', function(event){
				$('#step_two_instruction_2').fadeIn('fast');
				$('#ifb').hide();
			});
		} else {
			$('#step_two_instruction_2').fadeOut('fast', function(event){
				$('#step_two_instruction_1').fadeIn('fast');
				$('#ifb').show();
			});
		}
	});
	
	// add fields
	$('#add_field_bn').click(function(event){
		$('#add_field_bn').fadeOut('fast');
		$('#step_two_bn').fadeOut('fast', function(event) {
			$('.field-div').append(
				'<input autofocus class="field form-control" type="text" size="15" size="10" placeholder="fieldname">' +
				'<div class="field-badge form-control">' +
					'<span class="badge">0</span>' +
				'</div>' +
				'<div class="field-delete form-control" style="cursor: pointer">' +
					'<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>' +
				'</div>');
			$('.field').last().focus();
			$('#step_two_instruction_1').show();
			$('#ifb').show();
		});
	});
	
	// delete fields
	$('#fields').on('click', '.field-delete', function(event){
		var curr_i = $(this).index('.field-delete');
		if ($('.field:eq(' + curr_i + ')').prop('disabled') == false) {
			$('#done_bn').hide();
			$('#step_two_instruction_2').hide();
			$('#step_two_instruction_1').hide();
			$('#add_field_bn').fadeIn('fast');
			$('#step_two_bn').fadeIn();
			$('#ifb').show();
		}
		$('.field:eq(' + curr_i + ')').remove();
		$('.field-badge:eq(' + curr_i + ')').empty();
		$('.field-badge:eq(' + curr_i + ')').remove();
		$('.field-delete:eq(' + curr_i + ')').remove();
		if (field_xpaths.length != 0) {
			field_xpaths.splice(curr_i, 1);
		}
		refined_xpath = "";
		sample_xpaths = [];
		candidate_xpaths = [];

		if ($('.field').length == 0) {
			$('#step_two_bn').hide();
			$('#done_bn').hide();
			$('#step_two_instruction_2').hide();
			$('#step_two_instruction_1').fadeOut('fast', function(event){
				$('#add_field_bn').fadeIn('fast');
			});
		}
//		alert($('#iframe').contents().xpath(getElementTreeXPathNode(event.target)).html());
//		alert(
//				document.getElementById('iframe').contentWindow.document.evaluate(
//						getElementTreeXPathNode(event.target),
//						document.getElementById('iframe').contentWindow.document,
//						null,
//						XPathResult.FIRST_ORDERED_NODE_TYPE,
//						null).singleNodeValue.textContent
//			);
	});
	
	// done selecting datas
	$('#done_bn').click(function(event) {
		$('#done_bn').fadeOut('fast', function(event){
			field_xpaths.push(refined_xpath);
			refined_xpath = "";
			sample_xpaths = [];
			candidate_xpaths = [];
			$('.field').attr('disabled','disabled');
			$('#ifb').show();
			$('#add_field_bn').fadeIn('fast');
			$('#step_two_bn').fadeIn('fast');
			$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
		});
	});
	
	// push to field_xpaths
	$('#step_two_bn').click(function(event) {
		var crawlerTemplate = []
		$(".field").each(function(i){
			if ($(this).val() != "" && field_xpaths[i] != "") {
				crawlerTemplate.push('"' + $(this).val() + '":"' + field_xpaths[i] + '"');
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
	
	// show loader after submit form
	$('#create').submit(function( event ) {
		$('#step_three_bn').fadeOut('fast', function(event) {
			$('#loader').fadeIn('fast');
		});
	});
	
	/***************** DATA SECTION *****************/	
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
