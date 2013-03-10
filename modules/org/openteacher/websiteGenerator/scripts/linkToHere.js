$(document).ready(function() {
	$(document).on('click', '.linkToLinkHere', function() {
		$(this).hide()
		$('#currentPage').html(currentPage);
		$('#linkHere').show();
	});
});