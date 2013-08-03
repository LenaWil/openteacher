function renderTemplate(id, data) {
	var template = $(id).text();
	var result = "";
	var evalingStart = null;
	var i = 0;

	while (i < template.length) {
		if (template[i] === "@" && template[i + 1] === "!") {
			evalingStart = i + 2;
		}
		if (evalingStart === null) {
			result += template[i];
		}
		if (template[i - 1] === "!" && template[i] === "@") {
			var expr = template.substring(evalingStart, i - 1);
			var exprResult = (function () {
				for (var key in data) {
					eval("var " + key + " = data['"+ key + "'];");
				}
				return eval(expr);
			}());
			result += exprResult;
			evalingStart = null;
		}
		i += 1;
	}

	return result;
}
