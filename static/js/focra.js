$(document).ready(function() {
	
	/************* Create Crawler Steps **************/
	var first = false;
	if ($('#first').length) {
		first = true;
	}
	
	function showStepOne() {
		if (first) {
			hidePopovers();
		}
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
	var shownFirst = false;
	function showStepTwo() {
		$('#ifb').show();
		$('#toggleDiv').hide();
		$('#step_one').hide();
		$('#step_three').hide();
		$('#step_two').fadeIn('fast');
		
		if (first && shownFirst == false) {
			shownFirst = true;
			hidePopovers($('#firstField'));
		}
	}
	
	var shownCrawlerName = false;
	function showStepThree() {
		$('#step_one').hide();
		$('#step_two').hide();
		$("#step_three").fadeIn('fast', function(event) {
			$('#crawlerName').focus();
		});
		$('#toggleDiv').hide();
		if (first && shownCrawlerName == false) {
			shownCrawlerName = true;
			hidePopovers($('#crawlerName'));
		}
	}
	
	/*********** STEP 1 ************/
	var js = true;
	var css = true;
	
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
	
	// step 1 on page load
	if (first) {
		$('#url').popover('show');
	}
	
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
				$('#url').popover('hide');
				$('#step_one_bn').popover('show');
				shown1 = true;
			}
		} else {
			if (first) {
				$('#step_one_bn').popover('hide');
				$('#url').popover('show');
				shown1 = false;
			}
			$('#step_one_bn').hide();
			$('#step_one_instruction').fadeIn('fast');
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
				$('#url').popover('destroy');
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

	var shownBadge = false;
	// iframe on load
	$('#iframe').load(function(){
		if ($('#iframe').attr('srcdoc') != '') {
			
			$('#loader').fadeOut('fast', function(event) {	
				showStepTwo();
				// for chain crawler
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
			
			var contain_texts = "";
			
			// mouse over event
			$(this.contentWindow.document).mouseover(function (event) {
								
				contain_texts = $(event.target).text().trim().length;

				if (pager_mode) {
					if (typeof $(event.target).attr('href') != 'undefined' && contain_texts != 0) {
						$(event.target).addClass( "outline-element" );
					}
				} else {
					if ($(event.target).prop('tagName').toLowerCase() == 'img' || contain_texts != 0) {
						$(event.target).addClass( "outline-element" );
					}
				}
			
			// mouse out event
			}).mouseout(function (event) {
				$(event.target).removeClass('outline-element');
			
			// on click event
			}).on('click dblclick', function (event) {
				
				if (first == true && pager_mode == false && shownBadge == false) {
					hidePopovers($('#firstBadge'));
					shownBadge = true;
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
						pager_mode = false;
						$('#pager_cancel_bn').hide();
						$('#step_three_bn').fadeIn('fast');
						$('#ifb').fadeIn('fast');
						$('#iframe').contents().find('.outline-element-clicked').removeClass('outline-element-clicked');
					}
				}
				/************** END *****************/
				
				else {
					
					//alert($(event.target).text());
					
					if ($(event.target).prop('tagName').toLowerCase() == 'img' || contain_texts != 0) {
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
			$('#firstField').popover('hide');
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
			if (first) {
				hidePopovers();
			}
		} else {
			$('#step_two_instruction_1').fadeIn('fast');
			$('#step_two_instruction_2').hide();
			$('#done_bn').hide();
			$('#ifb').fadeIn('fast');
			if (first) {
				hidePopovers();
			}
		}
	});

	// add fields
	$('#add_field_bn').click(function(event) {
		if (first) {
			hidePopovers();
		}
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
	});

	// delete fields
	$('#fields').on('click', '.field-delete', function(event) {
		if (first) {
			hidePopovers();
		}
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
	
	var shownDone = false;
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
		if (first && shownDone == false) {
			shownDone = true;
			hidePopovers($('#step_two_bn'));
		}
	});

	$('#step_two_bn').click(function(event) {
		if (first) {
			$('#firstField').popover('destroy');
			$('#iframe').popover('destroy');
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
		$('#step_three_bn').hide();
		$('#step_three_instruction').fadeIn('fast');
		$('#pager_cancel_bn').fadeIn('fast');
		$('#ifb').fadeOut('fast');
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
			
			/**** ADDED ****/
			var node1 = selected_xpaths[0].split('/');
			// get the text or src only
			if (node1[node1.length-1].replace(/[^a-z]/g,'').trim() != 'img' && node1[node1.length-1].replace(/[^a-z]/g,'').trim() != 'a') {
				//general_xpath += '//text()[normalize-space()]';
				general_xpath = '';
				for (n=1; n < node1.length; n++) {
					if (n == node1.length-1) {
						general_xpath += "//" + node1[n];
					} else {
						general_xpath += "/" + node1[n];
					}
				}
				general_xpath = general_xpath;
			}
			
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
				
				if (first && shownDone == false) {
					$('#firstBadge').popover('destroy');
					$('#done_bn').popover('show');
				}
				
				// we can find similar xpaths if diff is just one node
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
					} else if (node1[node1.length - 1].toLowerCase() == 'a') {
						if (typeof $('#iframe').contents().xpath(x + '[' + (i+1) + ']' + sub_x + '/@href').val() != 'undefined') {
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
				} else if (node1[node1.length-1].replace(/[^a-z]/g,'') == 'a') {
					//sub_x = sub_x + '/@href';
					sub_x = sub_x;
				} else {
					sub_x_split = sub_x.split('/');
					sub_x = '';
					for (s=1; s < sub_x_split.length; s++) {
						if (s == sub_x_split.length-1) {
							sub_x += "//" + sub_x_split[s];
						} else {
							sub_x += "/" + sub_x_split[s];
						}
					}
					sub_x = sub_x;
				}
				// remove tbody because its generated from browser
				general_xpath = (x + sub_x).replace(/\/tbody/g, '');
			} else {
				//if diff(node1, node2) > 1 we deselect and remove node1
				$('#iframe').contents().xpath(selected_xpaths[0]).removeClass('outline-element-clicked');
				selected_xpaths.splice(0, 1);
				// node2 will take over node1
				general_xpath = selected_xpaths[0].replace(/\/tbody/g, '');
				
				if (node1[node1.length-1].replace(/[^a-z]/g,'') != 'img' && node1[node1.length-1].replace(/[^a-z]/g,'') != 'a') {
					//general_xpath += '/descendant-or-self::text()[normalize-space()]';
					general_xpath = '';
					for (n=1; n < node1.length; n++) {
						if (n == node1.length-1) {
							general_xpath += "//" + node1[n];
						} else {
							general_xpath += "/" + node1[n];
						}
					}
					general_xpath = general_xpath;
				}
				
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
			
			var node1 = selected_xpaths[0].split('/');
			
			if (node1[node1.length-1].replace(/[^a-z]/g,'') != 'img' && node1[node1.length-1].replace(/[^a-z]/g,'') != 'a') {
				//general_xpath += '//text()[normalize-space()]';
				general_xpath = '';
				for (n=1; n < node1.length; n++) {
					if (n == node1.length-1) {
						general_xpath += "//" + node1[n];
					} else {
						general_xpath += "/" + node1[n];
					}
				}
				general_xpath = general_xpath;
			}
			
			candidate_xpaths = selected_xpaths;
		}
		
		return candidate_xpaths;
	}
	
	/************* CRAWLER SECTION ***************/
	var poll_stats;
	var INTERVAL = 1000;
	
	// poll on load, if it is not running it will stop automatically
	poll_stats = setInterval(function () {getStats()}, INTERVAL);
	
	// to toggle start stop crawler
	$('#switchBn').click(function(event) {
		if ($('#switchBn').html().indexOf('Start') >= 0 || $('#switchBn').html().indexOf('Restart') >= 0) {
			$('#switchBn').html('Starting..');
			$('#stateBn').hide();
			$('#switchBn').attr('disabled', true);
			$.ajax({
				url : '/start',
				type: 'POST',
				data : {
					csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
					'crawlerName': $('#crawlerName').val()
				},
				success: function( data ){
					if (data == "ParentDontExists") {
						$('#switchBn').html('Restart Crawl');
						$('#switchBn').removeAttr('disabled');
						$('#switchBn').removeClass('btn-danger').addClass('btn-success');
						$('#stateBn').hide();
						$('#alert').fadeIn('fast');
						setTimeout(function(){ $('#alert').fadeOut('fast'); }, 2000);
					} else {
						poll_stats = setInterval(function () {getStats()}, INTERVAL);
					}
				}
			});
		} else if ($('#switchBn').html().indexOf('Stop') >= 0) {
			$('#switchBn').html('Stopping..');
			$('#switchBn').attr('disabled', true);
			$.ajax({
				url : '/stop',
				type: 'POST',
				data : {
					csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
					'crawlerName': $('#crawlerName').val()
				}
			});	
		}
		
	});
	
	// pause crawler
	$('#stateBn').click(function(event) {
		if ($('#stateBn').html().indexOf('pause') >= 0) {
			$('#stateBn').html('Pausing..');
			$('#stateBn').attr('disabled', true);
			$.ajax({
				url : '/pause',
				type: 'POST',
				data : {
					csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
					'crawlerName': $('#crawlerName').val()
				}
			});
		} else if ($('#stateBn').html().indexOf('play') >= 0) {
			$('#stateBn').html('Resuming..');
			$('#stateBn').attr('disabled', true);
			$.ajax({
				url : '/resume',
				type: 'POST',
				data : {
					csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
					'crawlerName': $('#crawlerName').val()
				},
				success: function( data ){
					if (data == "ParentDontExists") {
						$('#switchBn').html('Restart Crawl');
						$('#switchBn').removeAttr('disabled');
						$('#switchBn').removeClass('btn-danger').addClass('btn-success');
						$('#stateBn').hide();
						$('#alert').fadeIn('fast');
						setTimeout(function(){ $('#alert').fadeOut('fast'); }, 2000);
					} else {
						poll_stats = setInterval(function () {getStats()}, INTERVAL);
					}
				}
			});
		}
	});
	
	// delete crawler
	$('#deleteBn').click(function(event) {
		$.ajax({
			url : '/delete',
			type: 'POST',
			data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
					'crawlerName': $('#crawlerName').val()
			},
			success: function( data ){
				window.location.href = "/"
			}
		});
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
		hidePopovers();
	});
	
	var oldRes = "";
	function getStats() {
		$.ajax({
			url: "/stats",
			type: "GET",
			data: {
				'crawlerName': $('#crawlerName').val()
			},
			success: function(res) {
				var stats = res.split(',');
				if (stats[0] == "running") {
					// update stats
					$("#status").removeClass().addClass('label label-success').html("Running");
					$("#crawledPages").html(stats[1]);
					$("#rowsInserted").html(stats[2]);
					$("#timeExecuted").html(Math.round(stats[3]));
					$('#deleteBn').attr('disabled', true);
					$('#exportBn').attr('disabled', true);
					// show state button
					$('#stateBn').html('Pause <span  class="glyphicon glyphicon-pause" aria-hidden="true"></span>');
					$('#stateBn').removeAttr('disabled');
					$('#switchBn').html('Stop Crawl <span class="glyphicon glyphicon-stop" aria-hidden="true"></span>');
					$('#switchBn').removeClass('btn-success').addClass('btn-danger');
					
					// change switch button
					$('#switchBn').html('Stop Crawl <span class="glyphicon glyphicon-stop" aria-hidden="true"></span>');
					$('#switchBn').removeAttr('disabled');
					$('#switchBn').removeClass('btn-success').addClass('btn-danger');
					$('#stateBn').fadeIn('fast');
					
				} else if (stats[0] == "stopped") {
					// update stats
					$("#status").removeClass().addClass('label label-danger').html("Stopped");
					$("#crawledPages").html(stats[1]);
					$("#rowsInserted").html(stats[2]);
					$("#timeExecuted").html(Math.round(stats[3]));
					$('#deleteBn').removeAttr('disabled');
					$('#exportBn').removeAttr('disabled');
					
					// switch state to stop
					$('#switchBn').html('Restart Crawl');
					$('#switchBn').removeAttr('disabled');
					$('#switchBn').removeClass('btn-danger').addClass('btn-success');
					$('#stateBn').hide();
					if (oldRes == res) {
						clearInterval(poll_stats);
					}
				} else if (stats[0] == "paused") {
					// update stats
					$("#status").removeClass().addClass('label label-warning').html("Paused");
					$("#crawledPages").html(stats[1]);
					$("#rowsInserted").html(stats[2]);
					$("#timeExecuted").html(Math.round(stats[3]));
					$('#deleteBn').removeAttr('disabled');
					$('#exportBn').removeAttr('disabled');
					
					// show resume button
					$('#stateBn').html('Resume <span class="glyphicon glyphicon-play" aria-hidden="true"></span>');
					$('#stateBn').removeAttr('disabled');
					$('#switchBn').html('Restart Crawl');
					$('#switchBn').removeClass('btn-danger').addClass('btn-success');
					if (oldRes == res) {
						clearInterval(poll_stats);
					}
				} else if (stats[0] == "completed") {
					// update stats
					$("#status").removeClass().addClass('label label-primary').html("Completed");
					$("#crawledPages").html(stats[1]);
					$("#rowsInserted").html(stats[2]);
					$("#timeExecuted").html(Math.round(stats[3]));
					$('#deleteBn').removeAttr('disabled');
					$('#exportBn').removeAttr('disabled');
					
					if ($('#switchBn').prop('disabled') == false) {
						$('#switchBn').html('Restart Crawl');
						$('#switchBn').removeClass('btn-danger').addClass('btn-success');
						$('#stateBn').hide();
					}
					if (oldRes == res) {
						clearInterval(poll_stats);
					}
				} else {
					clearInterval(poll_stats);
				}
				oldRes = res;
			}
		});
	}
	
	/***************** CHAIN SECTION *****************/
	$(".fieldLinks").click(function(event) {
		var field = $(this).html()
		$('#chainText').html(field);
		$.ajax({
			url : '/chain',
			type: 'GET',
			data : {
				'field': field,
				'crawlerName': $('#crawlerName').val()
			},
			success: function(res){
				var data = $.parseJSON(res);
				$('#chainLinks').html("");
				$.each(data, function(i, obj) {
					if ($(obj[field]).text().replace(/\s/g, "") != "") {
						$('#chainLinks').append(
							"<tr class='chainURL' data-link='" + $(obj[field]).attr('href') + "'><td><a>" + $(obj[field]).text() + "</a></td></tr>"	
						);
					} else {
						$('#chainLinks').append(
							"<tr class='chainURL' data-link='" + $(obj[field]).attr('href') + "'><td><a>" + $(obj[field]).attr('href') + "</a></td></tr>"	
						);
					}
				});
				if ($('#chainLinks').html() == "") {
					$('#chainLinks').append(
						"<tr><td>No links Available</td></tr>"	
					);
				}
			}
		});
	});
	
	$('#chainLinks').on('click', '.chainURL', function(event) {
		$('#chainSelectedURL').val($(this).attr('data-link'));
		$('#chainJS').val(js);
		$('#chainCSS').val(css);
		$('#chainField').val($('#chainText').html());
		$('#chainParent').val($('#crawlerName').val());
		$('#chain').submit();
	});
	
	if ($('#chainURL').val()) {
		$('#step_two_instruction_1').hide()
		$('.field').attr('readonly', true);
		$('#loader').fadeIn('slow');
		fetchURL($('#chainURL').val(), $('#chainJS').val(), $('#chainCSS').val());
	}
	
	/******* TUTORIAL ************/
	function hidePopovers(showDOM) {
		$('#crawlerName').popover('hide');
		$('#url').popover('hide');
		$('#iframe').popover('hide');
		$('#firstField').popover('hide');
		$('#done_bn').popover('hide');
		$('#firstBadge').popover('hide');
		$('#step_two_bn').popover('hide');
		$('#step_one_bn').popover('hide');
		if (showDOM) {
			$(showDOM).popover('show');
		}
	}
	
	/******** EXPORT EXCEL *********/	
	$('#exportBn').click(function(event) {
		$('#export').submit();
	});
	
});
