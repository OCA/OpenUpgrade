<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
    
<head>
	<title>Live Chat</title>
	<script type="text/javascript" src="/static/javascript/MochiKit.js"></script>	
	<script type="text/javascript" src="/static/javascript/crm_designer.js"></script>	
	<!--
	<script type="text/javascript">
	function start_pop()
	{
	  
	    alert("Not logged");
	    	
		my_window=window.open("mywindow",'welcome','width=900,height=600,resizable=yes scrollbars=yes');
		
	}
	</script> -->
	
	<script type="text/javascript" src="/static/javascript/crm_designer.js"></script> 
</head>    

<body>	
<!--<form action="/select_topic">
		<input type="submit" value="Start Chat" ></input>
</form>
		--><table>
			<tr>
				<td>
						<a py:for="name in topiclist" onclick='topicsel(${name["id"]})'>${name['name']}</a>
				</td>
			</tr>
		</table>
		
</body>
</html>