function (doc, req) {
	doc = JSON.parse(req.body);
	doc._id = req.uuid;
	doc.lastEdited = new Date();
	return [doc, toJSON(doc)];
}
