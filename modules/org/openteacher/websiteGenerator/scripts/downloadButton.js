$(document).ready(function() {
	var onpageChange;

	onPageChange = function () {
		// Set download button
		$('#osStr').html(osStr);
		$('#downloadButton').css('background-image', 'url(../images/downloadbuttons/' + os + '-button.png');
		$("#downloadButton").attr('href', downloadLinks[os]);
	}
	// Loading is 'changing' the page too.
	onPageChange();
	$(document).on('pageChange', onPageChange);

	// On mouseover
	$(document).on('mouseover mouseleave', "#downloadButton", function(event){
		var buttonImage;
		if (event.type == 'mouseover') {
			buttonImage = 'url(../images/downloadbuttons/' + os + '-button-h.png)';
			$(this).css('background-image', buttonImage);
		}
		else
		{
			buttonImage = 'url(../images/downloadbuttons/' + os + '-button.png)';
			$(this).css('background-image', buttonImage);
		}
	});
	// On click
	$(document).on('click', '#toTheDownloadPage', function(event) {
		event.preventDefault();
		loadPage('download');
	});
});
