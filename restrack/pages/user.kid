<?xml version="1.0" encoding="utf-8" ?>
<!-- See http://www.kid-templating.org/language.html -->
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<?python
request.header('Content-Type', 'text/html')
?>
	<head>
		<title>User Info - ${user.name}</title>
	</head>
	<body>
		<!--pre py:content="repr(user)" /-->
		<h1>${user.name}</h1>
		<div class="infobit"><span>Email:</span> ${user.email}</div>
		<fieldset py:if="user.aemail">
			<legend>Administrator Info</legend>
			<div class="infobit" py:if="user.title"><span>Title:</span> ${user.title}</div>
			<div class="infobit"><span>SuperAdmin:</span> ${user.super}</div>
		</fieldset>
		<fieldset py:if="user.semail">
			<legend>Student Info</legend>
			<div class="infobit" py:if="user.year"><span>Year:</span> ${user.year}</div>
			<div class="infobit" py:if="user.majors"><span>Majors:</span> <span py:replace="', '.join(user.majors)" /></div>
			<div class="infobit" py:if="not user.majors"><span>Majors:</span> Undeclared</div>
		</fieldset>
		<fieldset py:if="user.cemail">
			<legend>Club Info</legend>
			<div class="infobit" py:if="user.description"><span>Description:</span> ${user.description}</div>
			<div class="infobit" py:if="user.class_"><span>SGA Class:</span> ${user.class_}</div>
		</fieldset>
	</body>
</html>
