<?php
	$lang = $_SERVER['HTTP_ACCEPT_LANGUAGE'];
	$filename = basename($lang) . ".html";
	if file_exists($filename) {
		require(file);
	} else {
		require("en.html");
	};
?>
