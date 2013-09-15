// Switches to another page
function loadPage(pageName)
{
	// Make the light go to the right place
	selectedMenuItem = '#' + pageName.split('/')[0] + 'Link';
	lightMove(selectedMenuItem);

	$("#content").slideUp(200,function() {
		$(this).load(pageName + '.contentonly.html', function() {
			$(this).slideDown(200);
			currentPage = pageName;
			$(document).trigger("pageChange");
		});
	});
}

$(document).ready(function() {
	// Makes the buttons functional
	$(document).on("click", ".aLink", function(event) {
		event.preventDefault();
		var rel = $(this).attr('rel');
		loadPage(rel);
	});
});
