<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
<!--<meta http-equiv="Refresh" content="4"></meta>-->
	<title>Chat</title>
</head>
<body>
	<ul>
		<li py:for="msg in msgs">${msg}</li>
	</ul>

</body>
</html>