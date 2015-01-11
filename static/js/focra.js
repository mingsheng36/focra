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

	// fetch a page based on url
	$('#fetchBn').click(function(event){
		//event.preventDefault();
		$.ajax({
			url: "/fetch",
			data: { 
				"url": $('#url').val(), 
			},
			type: "GET",
			success: function(res) {
				$('#iframe').attr('srcdoc', res);
				$('#templates').empty();
			}
		});

	});
	
	// add crawler template into form before submit crawler
	$('#create').submit(function( event ) {
		var crawlerTemplate = []
		$(".template_field").each(function(){
			if ($(this).find('.field').val() != "" || $(this).find('.xpath').val() != "") {
				crawlerTemplate.push('"' + $(this).find('.field').val() + '":"' + $(this).find('.xpath').val() + '"');
			}
		});
		$('#crawlerTemplate').val('{' + crawlerTemplate.toString() + '}');
	});

	// iframe event handlers for visual selection
	var fieldnum = 0
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
				fieldnum += 1;
				$('#templates').append('<div class="template_field">' + 
						'Field: <input class="field" type="text" value="field' + fieldnum +'" size="10" placeholder="e.g. MySpider">  ' +
						'XPath: <input class="xpath" type="text" value="' + getElementTreeXPath(event.target) +'"size="80" placeholder="e.g. MySpider">' +
						'<br/><br/></div>'
				);
				
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
