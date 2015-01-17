$(document).ready(function() {
	
	/************* Create Crawler Events **************/
	function showStepOne() {
		$('#step_two').hide();
		$('#step_three').hide();
		$('#step_one').fadeIn();
		$('#step_one_bn').fadeIn();
		$('#url').fadeIn();
		$('#url').prop('disabled', false);
		if ($('#url').val() != "") {
			$('#step_one_instruction').hide();
			$('#step_one_bn').fadeIn('fast');
		}
		$('#url').focus();
		// reset step 2
		$('#iframe').attr('srcdoc', "");
		$('#fields').empty();
		$('.field-div').append(
				'<input autofocus class="field form-control" type="text" size="15" size="10" placeholder="fieldname">' +
				'<div class="field-badge form-control">' +
				'<span class="badge">0</span>' +
				'</div>' +
				'<div class="field-delete form-control" style="cursor: pointer">' +
				'<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>' +
		'</div>');
		$('#step_two_instruction_2').hide();
		$('#done_bn').hide()
		$('#add_field_bn').hide();
		$('#step_two_bn').hide();
	}

	function showStepTwo() {
		$('#step_one').hide();
		$('#step_three').hide();
		$('#step_two').fadeIn('fast', function (event) {
			$('.field').focus();
		});
	}
	
	function showStepThree() {
		$('#step_one').hide();
		$('#step_two').hide();
		$("#step_three").fadeIn('fast', function(event) {
			$('#crawlerName').focus();
		});
	}
	
	// step 1 (url)
	$('#step_one_bn').click(function(event) {
		if ($('#url').val() != '') {
			$('#step_one_bn').fadeOut('fast', function(event) {
				fetchURL()
			});
		} else {
			alert('Please enter your URL');
		}
	});
	
	if ($('#url').val() != '') {
		$('#url').prop('disabled', false);
		$('#step_one_instruction').hide();
		$('#step_one_bn').show();
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
		if ($('#iframe').attr('srcdoc') != '') {
			$('#loader').fadeOut('fast', function(event) {	
				showStepTwo();
				$('#url').prop('disabled', false);
			});
			var contain_texts;
			$(this.contentWindow.document).mouseover(function (event) {
				contain_texts = $(event.target).clone().children().remove().end().text();
				if ($(event.target).prop("tagName").toLowerCase() == "img") {
					//$('#display').html($(event.target).attr("src").toLowerCase());
					$(event.target).addClass( "outline-element" );
				} 
				else if (contain_texts.trim()) {
					//$('#display').html(contain_texts);
					$(event.target).addClass( "outline-element" );
				}
			}).mouseout(function (event) {
				$(event.target).removeClass('outline-element');
			}).click(function (event) {
				if ($(event.target).prop("tagName").toLowerCase() == 'img' || contain_texts.trim()) {
					$(event.target).toggleClass('outline-element-clicked');

					sample_xpaths.push(getElementTreeXPathNode(event.target));
					candidate_xpaths = get_candidate_xpaths(sample_xpaths);

					$('.badge').last().html(candidate_xpaths.length);

					if ($('.field').val() != "" && field_xpaths[0] != "") {
						$('#step_two_instruction_2').fadeOut('fast', function(event){
							$('#done_bn').fadeIn('fast');
						});
					}
				}
			});
		}
	});
	
	// fields input change detector
	$('#fields').on('input propertychange','.field', function(event){	
		if ($(this).val() != "") {
			$('#step_two_instruction_1').fadeOut('fast', function(event){
				$('#step_two_instruction_2').fadeIn('fast');
				$('#ifb').hide();
			});
		} else {
			$('#step_two_instruction_2').fadeOut('fast', function(event){
				$('#step_two_instruction_1').fadeIn('fast');
				$('#ifb').show();
				$('#done_bn').hide();
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
			$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
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
	
	$('#step_two_bn').click(function(event) {
		var crawlerTemplate = []
		$(".field").each(function(i){
			if ($(this).val() != "" && field_xpaths[i] != "") {
				// push to field_xpaths
				crawlerTemplate.push('"' + $(this).val() + '":"' + field_xpaths[i] + '"');
			}
		});
		// add crawler template into form
		$('#crawlerTemplate').val('{' + crawlerTemplate.toString() + '}');
		showStepThree();
	});
	
	// step 3 (crawler name)
	$('#crawlerName').on('input propertychange', function(event){
		if ($('#crawlerName').val() != "") {
			$('#step_three_bn').fadeIn('fast');
		} else {
			$('#step_three_bn').fadeOut('fast');
		}
	});

	$('#step_three_bn').click(function(event) {
		$('#step_three_bn').fadeOut('fast', function(event) {
			$('#loader').fadeIn('fast');
			$('#create').submit();
		});
	});

	/**************** Key Press Events **************/
	$(document).keydown(function(event){
		switch(event.which) {
		case 8:	
			if(event.target.tagName.toLowerCase() != 'input' && $('#step_two').attr('style') != 'display: none;') {
				event.preventDefault();
				showStepOne();
			} else if (event.target.tagName.toLowerCase() != 'input' && $('#step_three').attr('style') != 'display: none;') {
				event.preventDefault();
				showStepTwo();
			}
			break;
		case 13:
			if ($('#step_one').attr('style') != 'display: none;') {
				if ($('#step_one_bn').attr('style') != 'display: none;') {
					$('#step_one_bn').trigger('click');
				}
			} else if ($('#step_two').attr('style') != 'display: none;') {	
				if ($('#step_two_bn').attr('style') != 'display: none;') {
					$('#step_two_bn').trigger('click');
				}
			} else if ($('#step_three').attr('style') != 'display: none;') {
				if ($('#step_three_bn').attr('style') != 'display: none;') {
					$('#step_three_bn').trigger('click');
				}
			}
			break;
		default: 
			break
		}
	});
	
	/*********** Helper functions **************/	
	// fetch URLs
	function fetchURL() {
		$('#step_one_bn').fadeOut('fast', function(event){
			$('#step_one_bn').hide();
			$('#url').prop('disabled', true);
			$('#loader').fadeIn('fast');
			$.ajax({
				url: "/fetch",
				data: { 
					"url": $('#url').val(), 
				},
				type: "GET",
				success: function(res) {
					$('#iframe').attr('srcdoc', res);
				}
			});
		});
	}
	
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
	
	// Interactive Web-Wrapper Construction for Extracting Relational Information from Web documents 
	// returns a list of candidate_xpaths
	function get_candidate_xpaths(sample_xpaths) {
		var candidate_xpaths = [];
		if (sample_xpaths.length == 1) {
			// always update refined_xpath before returning candidates
			refined_xpath = sample_xpaths[0];
			candidate_xpaths = sample_xpaths;
			return candidate_xpaths;
		} else if (sample_xpaths.length == 2) {
			// Generalization
			// break down into individual nodes
			var node1 = sample_xpaths[0].split('/');
			var node2 = sample_xpaths[1].split('/');
			node1.splice(0, 1);
			node2.splice(0, 1);
			var diff = [];
			for (i = 0; i < node1.length; i++) {
				if (node1[i] != node2[i]) {
					diff.push(i);
				}
			}
			var x = '';
			var sub_x = '';
			if (diff.length == 0) {
				// probably selecting the same element to 'deselect' that element
				// clear the sample_xpath
				sample_xpaths = [];
				refined_xpath = "";
				candidate_xpaths = "";
			} else if (diff.length == 1) {
				for (j = 0; j <= diff[0]; j++) {
					if (j == diff[0]) {
						x = x + "/" + node1[j].replace(/[^a-z]/g,'');
					} else {
						x = x + "/" + node1[j];
					}
				}
				for (k = diff[0] + 1; k < node1.length; k++) {
					sub_x = sub_x + '/' + node1[k];
				}
				$('#iframe').contents().xpath(x).each(function(i) {
					// because div[1] always start from 1
					console.log( $('#iframe').contents().xpath(x + '[' + (i+1) + ']' + sub_x).html() );
					candidate_xpaths.push(x + '[' + (i+1) + ']' + sub_x);		
					$('#iframe').contents().xpath(x + '[' + (i+1) + ']' + sub_x).addClass('outline-element-clicked');		
				});
				for (z = 0; z < candidate_xpaths.length; z++) {
					console.log(candidate_xpaths[z]);
				}
				// remove tbody because its generated from mozilla
				absolute = x + sub_x;
				refined_xpath = absolute.replace(/\/tbody/g, '');
			} else {
				//if diff > 1 for (node1, node2) we deselect and remove node1
				$('#iframe').contents().xpath(sample_xpaths[0]).removeClass('outline-element-clicked');
				sample_xpaths.splice(0, 1);
				
				// node2 will take over node1
				refined_xpath = sample_xpaths[0].replace(/\/tbody/g, '');
				// no candidates, return a single node
				candidate_xpaths = sample_xpaths;
			}
		} else {	
			// sample_xpaths == 3, user not satisfied with candidate results
			// deselect all candidate_xpaths and remove them but exclude the newly select xpath
			$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
			sample_xpaths.splice(0, 2);
			$('#iframe').contents().xpath(sample_xpaths[0]).addClass('outline-element-clicked');
			
			refined_xpath = sample_xpaths[0].replace(/\/tbody/g, '');
			candidate_xpaths = sample_xpaths;
		}
		return candidate_xpaths;
	}
	
	/************* CRAWLER SECTION ***************/
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
	
	// delete crawler
	$('#delete').submit(function(event) {
		var choice = confirm("Are you sure you want to delete?");
		if (choice == false) {
			event.preventDefault();
		}
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
							for (j = 0; j < fields.length; j++) { 
								rowData = rowData + "<td>" + obj[fields[j]] + "</td>";
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
