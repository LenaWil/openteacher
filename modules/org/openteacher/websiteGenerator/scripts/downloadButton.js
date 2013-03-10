$(document).ready(function() {
	// Set download button
	$('#osStr').html('for ' + osStr);
	$('#downloadButton').css('background-image', 'url(../images/oslogos/' + os + '-button.png');
	// On mouseover
	$(document).on('mouseover mouseleave', "#downloadButton", function(event){
		if (event.type == 'mouseover') {
			var buttonImage = 'url(../images/' + os + '-button-h.png)';
			$(this).css('background-image', buttonImage);
		}
		else
		{
			var buttonImage = 'url(../images/' + os + '-button.png)';
			$(this).css('background-image', buttonImage);
		}
	});
	// On click
	$(document).on('click', '#toDownload', function(event) {
		event.preventDefault();
		loadPage('download');
	});
});