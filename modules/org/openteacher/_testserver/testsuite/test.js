/*
	Copyright 2011, Marten de Vries

	This file is part of OpenTeacher.

	OpenTeacher is free software: you can redistribute it and/or modify
	it under the terms of the GNU Affero General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	OpenTeacher is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.
*/

$.ajaxSetup({
	"async": false,
	"success": log_success,
	"error": log_error
});

function log_success(data) {
	log(data);
}

function log_error(data) {
	log(data.responseText);
}

function log(text) {
	$("#results").append("<li>" + text + "</li>");
}

function log_header(text) {
	log("<br /><strong>" + text + ":</strong>");
}

$(function() {
	log_header("(De)register and authentication");
	log("Logout while not logged in");
	$.post("/user/logout");
	log("Register a student, impossible because first an admin should be registered.")
	$.post("/user/register", {"username": "a", "hashed_password": "b", "role": "student"});
	log("Register the admin");
	$.post("/user/register", {"username": "a", "hashed_password": "b", "role": "admin"});
	log("Try to register a student with a different name");
	$.post("/user/register", {"username": "b", "hashed_password": "b", "role": "student"});
	log("Login as admin");
	$.post("/user/login", {"username": "a", "hashed_password": "b"});
	log("Try to register a student with the same name");
	$.post("/user/register", {"username": "a", "hashed_password": "b", "role": "student"});
	log("Try again to register a student with a different name");
	$.post("/user/register", {"username": "b", "hashed_password": "b", "role": "student"});
	log("Show info on the current logged in user (admin)");
	$.post("/user/me");
	log("Show info on all users");
	$.post("/user/");
	log("Logout");
	$.post("/user/logout");
	log("Try to deregister the user");
	$.post("/user/deregister", {"username": "b"});
	log("Login back in and deregister the student.");
	$.post("/user/login", {"username": "a", "hashed_password": "b"});
	$.post("/user/deregister", {"username": "b"});
	log("Log out again");
	$.post("/user/logout");

	log_header("Test groups");
	log("Log in as admin, and register 2 groups");
	$.post("/user/login", {"username": "a", "hashed_password": "b"});
	$.post("/group/register", {"short_name": "a"});
	$.post("/group/register", {"short_name": "b", "long_name": "B"});
	log("Register a student");
	$.post("/user/register", {"username": "b", "hashed_password": "b", "role": "student"});
	log("Add the student to group a and b and group b to group a");
	$.post("/group/add_user", {"group_id": 1, "user_id": 2});
	$.post("/group/add_user", {"group_id": 2, "user_id": 2});
	$.post("/group/add_group", {"parent_id": 1, "child_id": 2});
	log("Show the current contents of the group");
	$.post("/group/", {"short_name": "b"});
	$.post("/group/groups", {"short_name": "a"});
	$.post("/group/users", {"short_name": "a"});
	log("Remove the student from group b and deregister the student. This should automatically clean up the reference in group a");
	$.post("/group/remove_user", {"group_id": 2, "user_id": 2});
	$.post("/user/deregister", {"username": "b"});
	log("Remove group b from group a");
	$.post("/group/remove_group", {"parent_id": 1, "child_id": 2});
	log("Add it again and then remove group b. Reference should be cleaned up automatically.")
	$.post("/group/add_group", {"parent_id": 1, "child_id": 2});
	$.post("/group/deregister", {"id": 2});
	log("Also remove the remaining group and logout");
	$.post("/group/deregister", {"id": 1});
	$.post("/user/logout");

	log_header("Finally, remove the admin user");
	$.post("/user/login", {"username": "a", "hashed_password": "b"});
	$.post("/user/deregister", {"username": "a"});
	$.post("/user/logout");
});
