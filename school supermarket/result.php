
<html>
	<head>
		<title>School Supermarket</title>
		<link rel="stylesheet" href="css/style.css">
		<link href='http://fonts.googleapis.com/css?family=Bitter:400,700' rel='stylesheet' type='text/css'>
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
		
		<script>
		function schoolSearch(postcode) {
			console.log('http://greenarrow.dfeappathon.rewiredstate.org/cgi.php?postcode=' + encodeURIComponent(postcode));
			$.getJSON('http://greenarrow.dfeappathon.rewiredstate.org/cgi.php?postcode=' + encodeURIComponent(postcode), function(data) {
				var items = [];
				console.log(data);
				$.each(data, function(index, value) {
					var school = value.school;
					var stats = value.stats;
					console.log(school);
					items.push('<div class="result"><span id="name">' + school.school_name + '</span><span id="dis">' + school.distance.toFixed(2) + ' <span class="nextline">miles</span></span><div class="clear"></div><span id="ks4gen">' + ((stats.positive_outliers_k4 / stats.students_k4)*100).toFixed(2) + '%<span class="nextline">KS4 Geniuses</span></span><span id="ks5gen">' + ((stats.positive_outliers_k5 / stats.students_k5) * 100).toFixed(2) + '%<span class="nextline">KS5 Geniuses</span></span><span id="prog" class="pos">' + (((stats.positive_outliers_k4 / stats.students_k4)*100) - ((stats.positive_outliers_k4 / stats.students_k4)*100)).toFixed(2) + '%<span class="nextline">Progression</span></span></div>');
				});
				
				$("#wrapper").remove();

				$('<div/>', {
					'id': 'wrapper',
					html: items.join('')
				}).appendTo('body');

				$('<h3/>', {
					html: 'Results for <span id="searchparameter">' + postcode + '</span>'
				}).prependTo('#wrapper');
			});
		}
		function getURLParameter(name) {
		    return decodeURIComponent(
		        (location.search.match(RegExp("[?|&]"+name+'=(.+?)(&|$)'))||[,null])[1]
		    );  
		}
		
		$(document).ready(function () {
			schoolSearch(getURLParameter("postcode"));
		});
		
		$("#postcode-submit").click(function() {
			schoolSearch($("#postcode-input").val());
		});
		</script>
	</head>
	<body>
		<header>
			<a href="index.php"><img src="img/logo.png"></a>
			<form action="#">
				<input type="text" name="postcode" id="postcode-input">
				<input type="submit"  value="Search!" id="postcode-submit">
			</form>
			<p>Built at the 2<sup>nd</sup> DfE Appathon by <a href="http://twitter.com/puntofisso">GS</a>, <a href="http://twitter.com/craigsnowden">CS</a>, <a href="http://twitter.com/angel_nights">AJ</a> & <a href="http://twitter.com/phazonoverload">KL</a>.</p>
		</header>
		<div id="wrapper">
			<img src="img/ajax-loader.gif" style="text-align:center;"/>
		</div>
	</body>
</html>