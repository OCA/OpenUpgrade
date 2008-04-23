<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
    
<head>
	<title>Chat</title>
	<style type="text/css">
<!--
body {
margin: 0;
padding: 0;
height:100%;
width:100%;
}
#wrap {
position: absolute; /* Needed for Safari */
width: 100%;
height: 100%;
}
-->
</style> 
	<script type="text/javascript" src="/static/javascript/crm_designer.js"></script>
</head>
<body style="height: 100%; width: 100%;" onload="load();">
<form name="MyForm"><!--	
	<table  id="wrap" style="height: 98%; width:98%;" align="center">
			<tr >
					<td style="height:100%; width:100% ">
						<textarea id="chat_txt1" style="height:100%; width:100% " rows="7" cols="70" readonly="True">
						</textarea>
					</td>
			</tr>
			<hr/>
			<tr>
					<td id="request" style="height: 100%; width: 100%">
						<textarea name="chat_txt2" style="height:100%; width:100% " rows="3" cols="70" >
						</textarea>
					</td>
			</tr>
			
			
	</table>
-->
<table id="wrap" border='3px' >
	<tr style="height:100%" >
		<td width="90%">

		</td>
		<td width="10%">
		
		</td>		
	</tr>
	
	
	<tr style="height: 100%;">
		<td colspan="2" style="height: 100%">
		<span style="background-color: gray;">
			<textarea style="height: 100%; width:100%" id="text2" rows="3"></textarea>
		</span>
		</td>
	</tr>
	
</table>
</form>
<script type="text/javascript">
<!--
function getWindowHeight() {
	var windowHeight = 0;
	if (typeof(window.innerHeight) == 'number') 
	{
		windowHeight = window.innerHeight;
	}
	else 
	{
		if (document.documentElement && document.documentElement.clientHeight) 
		{
			windowHeight = document.documentElement.clientHeight;
		}
		else 
		{
			if (document.body && document.body.clientHeight) 
			{
				windowHeight = document.body.clientHeight;
			}
		}
	}
	return windowHeight;
	window.innerWidth	
}

function setWrap() 
{
	if (document.getElementById) 
	{
		var windowHeight = getWindowHeight();
		if (windowHeight > 0) 
		{
			var wrapElement = document.getElementById('wrap');
			wrapElement.style.position = 'absolute';
			wrapElement.style.height = (windowHeight-2) + 'px';

		}
	}
}

window.onload = function() 
{
	setWrap();
}

window.onresize = function() 
{
	setWrap();
}
//-->
</script>
</body>    
</html>
