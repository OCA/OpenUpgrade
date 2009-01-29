<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
</head>
<body>
	<br/><br/><br/>
	<div class="box2">
		<form action="/login/do_login/" method="post">
		    <table align="center" cellspacing="2px" border="0">
		        <tr>
		            <td class="label">User :</td>
		            <td><input type="text" id="user" name="user" style="width: 300px;"/></td>
		        </tr>
		        
		        <tr>
		            <td class="label">Password :</td>
		            <td><input type="password" id="password" name="password" style="width: 300px;"/></td>
		        </tr>
		        <tr>
		            <td></td>
		            <td align="right">
		            	<button type="button" style="width: 80px; white-space: nowrap">Registration</button>
		                <button type="submit" style="width: 80px; white-space: nowrap">Login</button>
		            </td>
		        </tr>
		    </table>
		</form>
	</div>
	
	<div py:if="message" class="box2 message">
		${message}
	</div>
</body>
</html>