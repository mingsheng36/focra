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

	// fetch a page based on url
	$('#fetchBn').click(function(event){
		event.preventDefault();
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

	// iframe event handlers for visual selection
	var fieldnum = 0
	$('#iframe').load(function(){
		$(this.contentWindow.document).mouseover(function (event) {
			if ($(event.target).prop("tagName").toLowerCase() == 'img') {
				$(event.target).addClass( "outline-element" );
			} 
			else if ($(event.target).clone().children().remove().end().text().trim()) {
				$('#display').html($(event.target).clone().children().remove().end().text());
				$(event.target).addClass( "outline-element" );
			}
		}).mouseout(function (event) {
			$(event.target).removeClass('outline-element');
		}).click(function (event) {
			$(event.target).toggleClass('outline-element-clicked');
			//alert(getXPath(event.target));
			fieldnum += 1;
			$('#template').append('<div class="row">' + 
					'Field: <input class="field" type="text" value="field' + fieldnum +'" size="10" placeholder="e.g. MySpider">  ' +
					'XPath: <input class="xpath" type="text" value="' + getElementTreeXPath(event.target) +'"size="40" placeholder="e.g. MySpider">' +
					'<br/><br/></div>'
			);
		});
	});	
	
	// function to get xpath from the iframe DOM object
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
	
// 	Firebug implementation of getting XPath
//	function getElementTreeXPath(element)
//	{
//	    var paths = [];
//	    // Use nodeName (instead of localName) so namespace prefix is included (if any).
//	    for (; element && element.nodeType == 1; element = element.parentNode)
//	    {
//	        var index = 0;
//	        for (var sibling = element.previousSibling; sibling; sibling = sibling.previousSibling)
//	        {
//	            // Ignore document type declaration.
//	            if (sibling.nodeType == Node.DOCUMENT_TYPE_NODE)
//	                continue;
//
//	            if (sibling.nodeName == element.nodeName)
//	                ++index;
//	        }
//
//	        var tagName = element.nodeName.toLowerCase();
//	        var pathIndex = (index ? "[" + (index+1) + "]" : "");
//	        paths.splice(0, 0, tagName + pathIndex);
//	    }
//	    return paths.length ? "/" + paths.join("/") : null;
//	};	
	
	// monitor section
	$('#monitorLink').click(function(){
		$('#dataDiv').hide();
		$('#settingsDiv').hide();
		$('#monitorDiv').show();
	});
	
	// load data section
	var loaded = false;
	var fields = [];
	$(".fields").each(function(){
		fields.push($(this).html());
	});
	
	$('#dataLink').click(function(){
		$('#monitorDiv').hide();
		$('#settingsDiv').hide();
		$('#dataDiv').show();
		
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
						$('#crawlerData').show();
					}
				}
			});
			
		}
	});
	
	// settings section
	$('#settingsLink').click(function(){
		$('#monitorDiv').hide();
		$('#dataDiv').hide();
		$('#settingsDiv').show();
	});

});
