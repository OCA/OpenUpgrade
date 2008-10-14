<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'master.kid'">

<head>
	<title>Live Chat</title>
	<script type="text/javascript" src="/static/javascript/crm_designer.js"></script>
	<script type="text/css" src="/static/css/style.css"></script>
	<script type="text/javascript" src="/static/javascript/crm_designer.js"></script>
</head>

<body>
<table width="100%" >
	<tr>
		<td style="border: 1px;" width="70%"></td>
		<td class="topiclist" align="left" style="border-top: 2px;">
		<div  py:for="name in topiclist" >
			<a href="#" onclick='topicsel(${name["id"]})'>${name['name']}</a><br/>
		</div>
		</td>
	</tr>
</table>

</body>
</html>