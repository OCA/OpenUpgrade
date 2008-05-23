<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="master.kid" >
<head>
</head>
<body style="height: 100%; width: 100%;" onload="load();">
<form name="MyForm" action="/chatfunc/justsend">
<table id="wrap" border='3px' >

	<tr id="trref" >
		<td id="tdref">
<!--		<iframe src="/chatfunc/chatbox" style="width:100%;height: 600px;border: 1px;"> </iframe>
-->
		<div id="refreshdiv" class="chatbox" style="overflow:auto; ">
		</div>
		 </td>
	</tr>
	<tr id="buttonref">
		<td>
			<input type="button" onclick="sendmsg();" value="Send" />


<!--		<td py:if="disp==1"> -->
<!--				<input type="button" name="close" onclick='close_chat()' value="Close" />-->
<!--		</td>-->

			<input type="button" id="close" name="close" onclick="close_chat(window)" value="Close Chat" />

		</td>

	</tr>
	<tr id="txtarearef">
		<td colspan="2" style="height: 100%">
		<span>
			<textarea name="txtarea" style="width:100%; background-color: activeborder;" id="text2" onkeypress="return submitenter(this,event)"></textarea>
		</span>
		</td>

	</tr>

</table>
</form>
<script type="text/javascript">
<!--

window.onload = function()
{
	setWrap();
	activate_refreshg();
}

window.onresize = function()
{
	setWrap();
}
/*

*/
//-->
</script>
</body>
</html>