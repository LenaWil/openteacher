var calculateAveragePercents, calculatePercents;

(function () {
	function ZeroDivisionError() {
		this.name = "ZeroDivisionError";
		this.message = "integer division or modulo by zero";
	}

	calculateAveragePercents = function (tests) {
		percents = map(calculatePercents, tests);
		percentSum = sum(percents);

		if (tests.length === 0) {
			throw new ZeroDivisionError();
		}
		return Math.round(percentSum / tests.length);
	};

	calculatePercents = function (test) {
		var results = map(function (result) {
			return result.result === "right" ? 1 : 0;
		}, test.results);
		var total = results.length;
		var amountRight = sum(results);

		if (total === 0) {
			throw new ZeroDivisionError();
		}
		return Math.round(amountRight / total * 100);
	};
}());
