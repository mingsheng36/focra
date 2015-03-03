$(document).ready(function() {
	
	/************* Create Crawler Steps **************/
	var first = false;
	if ($('#first').length) {
		first = true;
	}
	
	function showStepOne() {
		
		$('#crawlerName').popover('hide');
		$('#url').popover('hide');
		$('#step_one_bn').popover('hide');
		$('#iframe').popover('hide');
		$('#firstField').popover('hide');
		$('#done_bn').popover('hide');
		$('#firstBadge').popover('hide');
		$('#step_two_bn').popover('hide');
		
		$('#step_two').hide();
		$('#step_three').hide();
		$('#step_one').fadeIn();
		$('#step_one_bn').fadeIn();
		$('#url').fadeIn();
		$('#url').attr('readonly', false);
		if ($('#url').val() != "") {
			$('#step_one_instruction').hide();
			$('#step_one_bn').fadeIn('fast');
		}
		$('#url').focus();
		// reset step 2
		$('#iframe').attr('srcdoc', "");
		$('#fields').empty();
		$('#fields').append(
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
		$('#toggleDiv').show();
		
	}

	function showStepTwo() {
		$('#ifb').show();
		$('#toggleDiv').hide();
		$('#step_one').hide();
		$('#step_three').hide();
		$('#step_two').fadeIn('fast');
		
		if (first) {
			$('#crawlerName').popover('hide');
			$('#url').popover('hide');
			$('#step_one_bn').popover('hide');
			$('#iframe').popover('hide');
			$('#firstField').popover('hide');
			$('#done_bn').popover('hide');
			$('#firstBadge').popover('hide');
			$('#step_two_bn').popover('hide');
			
			$('#firstField').popover('show');
		}
	}
	
	function showStepThree() {
		$('#step_one').hide();
		$('#step_two').hide();
		$("#step_three").fadeIn('fast', function(event) {
			$('#crawlerName').focus();
		});
		$('#toggleDiv').hide();
		if (first) {
			//$('#crawlerName').popover('hide');
			$('#url').popover('hide');
			$('#step_one_bn').popover('hide');
			$('#iframe').popover('hide');
			$('#firstField').popover('hide');
			$('#done_bn').popover('hide');
			$('#firstBadge').popover('hide');
			$('#step_two_bn').popover('hide');
			
			$('#crawlerName').popover('show');
		}
	}
	
	/*********** STEP 1 ************/
	var js = true;
	var css = true;
	
	if (first) {
		$('#url').popover('show');
	}
	
	// step 1 on page load
	if ($('#url').val() != '') {
		$('#url').attr('readonly', false);
		$('#step_one_instruction').hide();
		$('#step_one_bn').show();
	}
	
	// url input change
	var shown1 = false;
	$('#url').on('input propertychange', function(event) {
		if ($('#url').val() != '') {
			$('#step_one_instruction').hide();
			$('#step_one_bn').fadeIn('fast');
			if (first == true && shown1 == false) {
				$('#url').popover('destroy');
				$('#step_one_bn').popover('show');
				shown1 = true;
			}
		} else {
			$('#step_one_bn').hide();
			$('#step_one_instruction').fadeIn('fast');
		}
	});
	
	$('#toggleJS').click(function(event) {
		if(js) {
			js = false;
			$('#toggleJS').html('JS (OFFed)');
		} else {
			js = true;
			$('#toggleJS').html('JS (ONed)')
		}
	});
	
	$('#toggleCSS').click(function(event) {
		if(css) {
			css = false;
			$('#toggleCSS').html('CSS (OFFed)');
		} else {
			css = true;
			$('#toggleCSS').html('CSS (ONed)');
		}
	});
	// step 1 (url)
	$('#step_one_bn').click(function(event) {
		if ($('#url').val() != '') {
			$('#url').attr('readonly', true);
			$('#step_one_bn').hide();
			$('#step_one_instruction').hide();
			$('#loader').fadeIn('slow');
			fetchURL($('#url').val(), js, css)
			if (first) {
				$('#step_one_bn').popover('destroy');
			}
		} else {
			alert('Please enter your URL');
		}
	});
	
	/*********** STEP 2 ************/
	var field_xpaths = [];
	var selected_xpaths = [];
	var general_xpath = "";
	var pager_mode = false;
	
	// step 2 on page load
	if ($('.field').length > 1 || $('.field').attr('readonly') == true) {
		$('#fields').empty();
		$('#fields').append(
				'<input autofocus class="field form-control" type="text" size="15" size="10" placeholder="fieldname">' +
				'<div class="field-badge form-control">' +
				'<span class="badge">0</span>' +
				'</div>' +
				'<div class="field-delete form-control" style="cursor: pointer">' +
				'<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>' +
		'</div>');
		$('#step_two_instruction_1').show();
		$('#step_two_instruction_2').hide();
		$('#done_bn').hide();
		$('#add_field_bn').hide();
		$('#step_two_bn').hide();
	} else {
		// only 1 .field
		$('.field').attr('readonly', false);
		$('.field').val('');
	}

	// iframe on load
	$('#iframe').load(function(){
		if ($('#iframe').attr('srcdoc') != '') {
			$('#loader').fadeOut('fast', function(event) {	
				showStepTwo();
				// for baby crawler
				$('#step_two').fadeIn('fast', function (event) {
					$('#step_two_instruction_1').show()
					$('.field').attr('readonly', false);
					$('.field').focus();
				});
				$('#url').attr('readonly', false);
			});
			$('#iframe').contents().find('a').click(function(event) {
	            event.preventDefault();
	        });
			var contain_texts;
			$(this.contentWindow.document).mouseover(function (event) {
				contain_texts = $(event.target).clone().children().remove().end().text().trim();
				if (pager_mode) {
					if (typeof $(event.target).attr('href') != 'undefined' && contain_texts != '') {
						$(event.target).addClass( "outline-element" );
					}
				} else {
					if ($(event.target).prop('tagName').toLowerCase() == 'img' || contain_texts != '') {
						$(event.target).addClass( "outline-element" );
					}
				}
				
			}).mouseout(function (event) {
				$(event.target).removeClass('outline-element');
			}).on('click dblclick', function (event) {
				if (first) {
					$('#iframe').popover('destroy');
					$('#firstBadge').popover('show');
				}
				
				/************** PAGER *****************/
				if (pager_mode) {					
					if ($(event.target).prop("tagName").toLowerCase() == 'a' || $(event.target).parent().prop("tagName").toLowerCase() == 'a') {
						if ($(event.target).prop("tagName").toLowerCase() == 'a') {
							$('#crawlerPager').val($(event.target).text().trim());
						} else if ($(event.target).parent().prop("tagName").toLowerCase() == 'a') {
							$('#crawlerPager').val($(event.target).get(0).outerHTML.trim());
						}
						$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
						$('#step_three_instruction').hide();
						$('#pager_done_bn').fadeIn('fast');
					}
				}
				/************** END *****************/
				
				else {
					if ($(event.target).prop('tagName').toLowerCase() == 'img' || contain_texts != '') {
						if ($(event.target).parent().prop('tagName').toLowerCase() == 'a') {
							$(event.target).parent().toggleClass('outline-element-clicked');
							selected_xpaths.push(getElementTreeXPath($(event.target).parent()));
						} else {
							$(event.target).toggleClass('outline-element-clicked');
							selected_xpaths.push(getElementTreeXPath(event.target));
						}
						
						$('.badge').last().html(get_candidate_xpaths(selected_xpaths).length);
						if ($('.field').last().val() != '' && $('.badge').last().text() != 0) {
							$('#step_two_instruction_2').hide();
							$('#done_bn').fadeIn('fast');
						} else {
							$('#done_bn').hide();
							$('#step_two_instruction_2').fadeIn('fast');
						}
					}
				}
			});
		}
	});
	
	// fields input change detector
	var shown2 = false;
	$('#fields').on('input propertychange','.field', function(event){
		if (first == true && shown2 == false) {
			$('#firstField').popover('destroy');
			$('#iframe').popover('show');
			shown2 = true;
		}
		var curr_field_index = $(this).index('.field');		
		if ($(this).val() != '' && $('.field-badge:eq(' + curr_field_index + ')').text() == 0) {
			$('#step_two_instruction_1').hide()
			$('#step_two_instruction_2').fadeIn('fast');
			$('#done_bn').hide();
			$('#ifb').hide();
		} else if ($(this).val() != '' && $('.field-badge:eq(' + curr_field_index + ')').text() != 0){
			$('#step_two_instruction_2').hide();
			$('#step_two_instruction_1').hide();
			$('#step_two_instruction_2').hide();
			$('#ifb').fadeOut('fast');
			$('#done_bn').fadeIn('fast');
		} else if ($(this).val() == '' && $('.field-badge:eq(' + curr_field_index + ')').text() != 0){
			$('#step_two_instruction_1').fadeIn('fast');
			$('#step_two_instruction_2').hide();
			$('#done_bn').hide();
			$('#ifb').fadeIn('fast');
		} else {
			$('#step_two_instruction_1').fadeIn('fast');
			$('#step_two_instruction_2').hide();
			$('#done_bn').hide();
			$('#ifb').fadeIn('fast');
		}
	});

	// add fields
	$('#add_field_bn').click(function(event) {
		$('#step_two_bn').hide();
		$('#add_field_bn').hide(); 
		$('#fields').append(
				'<input autofocus class="field form-control" type="text" size="15" size="10" maxlength="20" placeholder="fieldname">' +
				'<div class="field-badge form-control">' +
				'<span class="badge">0</span>' +
				'</div>' +
				'<div class="field-delete form-control" style="cursor: pointer">' +
				'<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>' +
		'</div>');
		$('.field').last().focus();
		$('#step_two_instruction_1').show();
		$('#ifb').show();
		if (first) {
			$('#done_bn').popover('destroy');
			$('#firstBadge').popover('destroy');
			$('#step_two_bn').popover('destroy');
		}
	});

	// delete fields
	$('#fields').on('click', '.field-delete', function(event) {
		var curr_i = $(this).index('.field-delete');
		$('.field:eq(' + curr_i + ')').remove();
		$('.field-badge:eq(' + curr_i + ')').empty();
		$('.field-badge:eq(' + curr_i + ')').remove();
		$('.field-delete:eq(' + curr_i + ')').remove();
		general_xpath = '';
		selected_xpaths = [];
		if (field_xpaths.length != 0 && typeof field_xpaths[curr_i] != 'undefined') {
			field_xpaths.splice(curr_i, 1);
		}
		if (($('.field').length == 0 && field_xpaths.length == 0)) {
			$('#step_two_bn').hide();
			$('#done_bn').hide();
			$('#step_two_instruction_2').hide();
			$('#step_two_instruction_1').hide();
			$('#add_field_bn').fadeIn('fast');
			$('#ifb').fadeIn('fast');
			$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
		} else if ($('.field').length > 0) {
			if ($('.field').last().attr('readonly') == 'readonly') {
				$('#step_two_instruction_2').hide();
				$('#step_two_instruction_1').hide();
				$('#done_bn').hide();
				$('#add_field_bn').fadeIn('fast');
				$('#step_two_bn').fadeIn('fast');
				$('#ifb').fadeIn('fast');
				$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
			} else {
				if ($('.field').last().val() != '' && $('.badge').last().text() == 0) {
					$('#step_two_instruction_1').hide();
					$('#step_two_instruction_2').show();
					$('#done_bn').hide();
					$('#add_field_bn').hide();
					$('#step_two_bn').hide();
					$('#ifb').fadeOut('fast');
				} else if ($('.field').last().val() != '' && $('.badge').last().text() != 0) {
					$('#step_two_instruction_1').hide();
					$('#step_two_instruction_2').hide();
					$('#done_bn').fadeIn('fast');
					$('#add_field_bn').hide();
					$('#step_two_bn').hide();
					$('#ifb').hide();
				} else {
					$('#step_two_instruction_1').show();
					$('#step_two_instruction_2').hide();
					$('#done_bn').hide();
					$('#add_field_bn').hide();
					$('#step_two_bn').hide();
					$('#ifb').hide();
				}
			}
		}
		
	});
	
	// done selecting data
	$('#done_bn').click(function(event) {
		$('#done_bn').hide()
		field_xpaths.push(general_xpath);
		general_xpath = '';
		selected_xpaths = [];
		$('.field').attr('readonly', true);
		$('#ifb').fadeIn('fast');
		$('#add_field_bn').fadeIn('fast');
		$('#step_two_bn').fadeIn('fast');
		$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
		if (first) {
			$('#done_bn').popover('destroy');
			$('#firstBadge').popover('destroy');
			$('#step_two_bn').popover('show');
		}
	});

	$('#step_two_bn').click(function(event) {
		if (first) {
			$('#done_bn').popover('destroy');
			$('#firstBadge').popover('destroy');
			$('#step_two_bn').popover('destroy');
		}
		var crawlerTemplate = []
		$(".field").each(function(i){
			if ($(this).val() != '' && field_xpaths[i] != '') {
				// push to field_xpaths
				crawlerTemplate.push('"' + $(this).val() + '":"' + field_xpaths[i] + '"');
			}
		});
		// add crawler template into form
		$('#crawlerTemplate').val('{' + crawlerTemplate.toString() + '}');
		showStepThree();
	});
	
	/*********** STEP 3 ************/
	// step 3 on page load
	if ($('#crawlerName').val() != '') {
		$('#crawlerName').attr('readonly', false);
		$('#pager_bn').fadeIn('fast');
		$('#step_three_bn').fadeIn('fast');
	} else {
		$('#pager_bn').hide();
		$('#step_three_bn').hide();
	}
	
	// check crawler name
	var cStatus = false;
	var shown3 = false;
	$('#crawlerName').on('input propertychange', function(event){
		if (first == true && shown3 == false) {
			$('#crawlerName').popover('show');
			shown3 = true;
		} else {
			$('#crawlerName').popover('destroy');
		}
		if (cStatus == false) {
			cStatus = true;
			if ($('#crawlerName').val() != '') {
				$('#step_three_check2').hide();
				$('#step_three_check').hide();
				$('#pager_bn').hide();
				$('#step_three_bn').hide();
				$('#loader').fadeIn('fast');
				setTimeout(function() { checkCrawlerName(); }, 700);
			} else {
				$('#step_three_check2').hide();
				$('#step_three_check').hide();
				$('#pager_bn').hide();
				$('#step_three_bn').hide();
				$('#feedback').removeClass('glyphicon-remove');
				$('#feedback').removeClass('glyphicon-ok');
				cStatus = false;
			}
		}
	});
	
	// show pagination option
	$('#pager_bn').click(function(event) {
		pager_mode = true;
		$('#crawlerName').attr('readonly', true);
		$('#pager_bn').hide();
		$('#pager_done_bn').hide();
		$('#step_three_bn').hide();
		$('#step_three_instruction').fadeIn('fast');
		$('#pager_cancel_bn').fadeIn('fast');
		$('#ifb').fadeOut('fast');
	});

	$('#pager_done_bn').click(function(event) {
		pager_mode = false;
		$('#pager_done_bn').hide();
		$('#pager_cancel_bn').hide();
		$('#step_three_bn').fadeIn('fast');
		$('#ifb').fadeIn('fast');
		$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
	});
	
	$('#pager_cancel_bn').click(function(event) {
		pager_mode = false;
		$('#pager_cancel_bn').hide()
		$('#pager_done_bn').hide();
		$('#step_three_instruction').hide();
		$('#crawlerName').attr('readonly', false);
		$('#pager_bn').fadeIn('fast');
		$('#step_three_bn').fadeIn('fast');
		$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
		$('#ifb').fadeIn('fast');
		$('#crawlerPager').val('null');
	});

	$('#step_three_bn').click(function(event) {
		$('#step_three_instruction').hide();
		$('#pager_bn').hide();
		$('#step_three_bn').hide();
		$('#crawlerName').attr('readonly', true);
		$('#loader').fadeIn('slow');
		$('#create').submit();
	});

	/**************** Key Press Events **************/
	$(document).keydown(function(event) {
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
	function fetchURL(url, js, css) {
		$.ajax({
			url: '/fetch',
			data: { 
				'url': url,
				'js': js,
				'css': css
			},
			statusCode: {
				500: function() {
					alert( "Focra Server Error" );
				}
			},
			type: 'GET',
			success: function(res) {
				// if response is longer than 50, it is most propably a well formed html response
				if (res.length > 50) {
					$('#iframe').show();
					$('#iframe').attr('srcdoc', res);
				} else if (res == 'format') {
					$('#loader').hide();
					$('#url').attr('readonly', false).val("");
					$('#step_one_instruction').removeClass('btn-info').addClass('btn-danger').html("Please enter the correct URL format").show();
				} else {
					$('#loader').hide();
					$('#url').attr('readonly', false).val("");
					$('#step_one_instruction').removeClass('btn-info').addClass('btn-danger').html(res + ": Please re-enter your URL").show();
				}
			}
		});
	}
	
	// function to get xpath node from the iframe DOM object
	function getElementTreeXPath(element) {
		var xpath_length = $(element).parents().andSelf().length;
		return '/' + $(element).parents().andSelf().map(function(i, obj) {
			var $this = $(this);
			var tagName = this.nodeName;
			if ($this.siblings(tagName).length > 0) {
				tagName += '[' + ($this.prevAll(tagName).length + 1) + ']';
			}
			return tagName;
		}).get().join('/').toLowerCase();
	};
	
	// Interactive Web-Wrapper Construction for Extracting Relational Information from Web documents 
	// returns a list of candidate_xpaths
	function get_candidate_xpaths(selected_xpaths) {
		var candidate_xpaths = [];
		if (selected_xpaths.length == 1) {
			// general_xpath need to remove tbody
			general_xpath = selected_xpaths[0].replace(/\/tbody/g, '');
			candidate_xpaths = selected_xpaths;
			return candidate_xpaths;
		} else if (selected_xpaths.length == 2) {
			// Generalization
			var node1 = selected_xpaths[0].split('/');
			var node2 = selected_xpaths[1].split('/');
			node1.splice(0, 1);
			node2.splice(0, 1);
			var diff = [];
			for (var i = 0; i < Math.max(node1.length, node2.length); i++) {
				if (node1[i] != node2[i]) {
					diff.push(i);
				}
			}
			var x = '';
			var sub_x = '';
			if (diff.length == 0) {
				// probably selecting the same element to 'deselect' that element
				// clear the selected_xpath
				selected_xpaths = [];
				general_xpath = '';
				candidate_xpaths = '';
			} else if (diff.length == 1) {
				// we can find similar xpaths if diff is just one node
				if (first) {
					$('#firstBadge').popover('destroy');
					$('#done_bn').popover('show');
				}
				
				for (var j = 0; j <= diff[0]; j++) {
					if (j == diff[0]) {
						x = x + '/' + node1[j].replace(/[^a-z]/g,'');
					} else {
						x = x + '/' + node1[j];
					}
				}
				// add the rest of the xpath into the generalized xpath
				for (var k = diff[0] + 1; k < node1.length; k++) {
					sub_x = sub_x + '/' + node1[k];
				}
				$('#iframe').contents().xpath(x).each(function(i) {
					// because div[x] always start from x = 1
					if (node1[node1.length - 1].toLowerCase() == 'img') {
						if (typeof $('#iframe').contents().xpath(x + '[' + (i+1) + ']' + sub_x + '/@src').val() != 'undefined') {
							candidate_xpaths.push(x + '[' + (i+1) + ']' + sub_x);
							$('#iframe').contents().xpath(x + '[' + (i+1) + ']' + sub_x).addClass('outline-element-clicked');
						}
					} else if ($('#iframe').contents().xpath(x + '[' + (i+1) + ']' + sub_x).text().trim() != '') {
						candidate_xpaths.push(x + '[' + (i+1) + ']' + sub_x);
						$('#iframe').contents().xpath(x + '[' + (i+1) + ']' + sub_x).addClass('outline-element-clicked');
					}		
				});
				
				// get the text or src only
				if (node1[node1.length-1].replace(/[^a-z]/g,'') == 'img') {
					//sub_x = sub_x + '/@src';
					sub_x = sub_x;
				} else if (node1[node1.length-1].replace(/[^a-z]/g,'') == 'a'){
					sub_x = sub_x;
				} else {
					sub_x = sub_x + '/text()';
				}
				// remove tbody because its generated from browser
				general_xpath = (x + sub_x).replace(/\/tbody/g, '');
			} else {
				//if diff(node1, node2) > 1 we deselect and remove node1
				$('#iframe').contents().xpath(selected_xpaths[0]).removeClass('outline-element-clicked');
				selected_xpaths.splice(0, 1);
				// node2 will take over node1
				general_xpath = selected_xpaths[0].replace(/\/tbody/g, '');
				// no candidates, return a single node
				candidate_xpaths = selected_xpaths;
			}
		} else {	
			// selected_xpaths == 3, user not satisfied with candidate results
			// deselect all candidate_xpaths and remove them but exclude the newly select xpath
			$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
			// remove the two old selected xpath
			selected_xpaths.splice(0, 2);
			$('#iframe').contents().xpath(selected_xpaths[0]).addClass('outline-element-clicked');
			general_xpath = selected_xpaths[0].replace(/\/tbody/g, '');
			candidate_xpaths = selected_xpaths;
		}
		return candidate_xpaths;
	}
	
	/************* CRAWLER SECTION ***************/
	// call to start crawler
	$('#switchBn').click(function(event) {
		$('#switchBn').html('Initializing..');
		$('#switchBn').attr('disabled', true);
		$.ajax({
			url : '/start',
			type: 'POST',
			data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
			success: function( data ){
				$('#switchBn').html('Stop Crawler');
				$('#switchBn').removeAttr('disabled');
				$('#switchBn').removeClass('btn-success').addClass('btn-danger');
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
				$('#stopBn').attr('disabled',true);
				$('#switchBn').removeAttr('disabled');
				$('#deleteBn').removeAttr('disabled');
			}
		});
	});
			
	// pause crawler
	$('#pauseBn').click(function(event) {
		$('#display').html('Pausing..');
		$.ajax({
			url : '/pause',
			type: 'POST',
			data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
			success: function( data ){
				$('#display').html(data);
			}
		});
	});
	
	// resume crawler
	$('#resumeBn').click(function(event) {
		$('#display').html('Resuming..');
		$.ajax({
			url : '/resume',
			type: 'POST',
			data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
			success: function( data ){
				$('#display').html(data);
			}
		});
	});
	
	// delete crawler
	$('#deleteBn').click(function(event) {
		var choice = confirm("Are you sure you want to delete?");
		if (choice == true) {
			$.ajax({
				url : '/delete',
				type: 'POST',
				data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
				success: function( data ){
					window.location.href = "/"
				}
			});
		}
	});
	
	// create baby crawler button
	$('#createBabyBn').click(function(event) {
		$('#createBabyBn').hide();
		$('#selectField').fadeIn('fast');
	});
	
	// create baby crawler button
	$('#cancelBabyBn').click(function(event) {
		$('#selectField').hide();
		$('#createBabyBn').fadeIn('fast');
	});
	
	/***************** BABY SECTION *****************/
	if ($('#extractedLink').val()) {
		$('#step_two_instruction_1').hide()
		$('.field').attr('readonly', true);
		$('#loader').fadeIn('slow');
		fetchURL($('#extractedLink').val(), true, true)
	}
	
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
							for (var j = 0; j < fields.length; j++) { 
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

	/***************** Crawler Name checker *****************/
	function checkCrawlerName() {
		var name = $('#crawlerName').val()
		if(/^[a-zA-Z0-9]*$/.test(name) == true) {
			$('#step_three_check2').hide();
			$('#pager_bn').hide();
			$('#step_three_bn').hide();
			$.ajax({
				url : '/check',
				type: 'GET',
				data : {
					'crawlerName': name,
				},
				success: function( data ){
					$('#loader').hide();
					if (data == 'valid' && $('#crawlerName').val() != '') {
						$('#step_three_check').hide();
						$('#pager_bn').fadeIn('fast');
						$('#step_three_bn').fadeIn('fast');
						$('#feedback').removeClass('glyphicon-remove').addClass('glyphicon-ok');
						cStatus = false;
					} else if (data == 'invalid' && $('#crawlerName').val() != '') {
						$('#step_three_check').fadeIn('fast');
						$('#pager_bn').hide();
						$('#step_three_bn').hide();
						$('#feedback').removeClass('glyphicon-ok').addClass('glyphicon-remove');
						cStatus = false;
					} else {
						$('#step_three_check2').hide();
						$('#step_three_check').hide();
						$('#pager_bn').hide();
						$('#step_three_bn').hide();
						$('#feedback').removeClass('glyphicon-remove');
						$('#feedback').removeClass('glyphicon-ok');
						cStatus = false;
					}
				}
			});

		} else {
			$('#loader').hide();
			$('#step_three_check').hide();
			$('#step_three_check2').fadeIn('fast');
			$('#pager_bn').hide();
			$('#step_three_bn').hide();
			$('#feedback').removeClass('glyphicon-ok').addClass('glyphicon-remove');
			cStatus = false;
		}
	}
	
	$('#back2').click(function(event){
		showStepOne();
	});
	
	$('#back3').click(function(event){
		showStepTwo();
	});
	
});
