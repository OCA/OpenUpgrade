<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
	<title>Select a topic</title>
	<script type="text/javascript" src="/static/javascript/crm_designer.js"></script>
</head>
<body>
	<form id="topic_form" action="/start_chat">
		<table>
			<tr>
				<td>
						<a py:for="name in topiclist" onclick='topicsel(${name["id"]})'>${name['name']}</a>
				</td>
			</tr>
		</table>
	</form>
</body>
</html>