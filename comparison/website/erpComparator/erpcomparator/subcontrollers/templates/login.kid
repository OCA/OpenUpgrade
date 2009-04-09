
<div id="box" class="new_box" xmlns:py="http://purl.org/kid/ns#">
	<div py:if="error" id="error_box" align="center">
		<div class="box2 message">
			${error}
		</div>
	</div>
	<div align="center">
		<input type="radio" name="login" id="registered_user" onclick="if(getElement('registered').style.display == 'none') {getElement('registered').style.display = 'block'} else {getElement('registered').style.display = 'none'} if(getElement('new_registration').style.display == 'block' || getElement('new_registration').style.display == '') {getElement('new_registration').style.display = 'none'}"/> Already Registered  
		<input type="radio" name="login" id="new_user" onclick="if(getElement('new_registration').style.display == 'none') {getElement('new_registration').style.display = 'block'} else {getElement('new_registration').style.display = 'none'} if(getElement('registered').style.display == 'block' || getElement('registered').style.display == '') {getElement('registered').style.display = 'none'}"/> New Registration
	</div>
	<div id="registered" style="display:none;">
		<div class="header">
		<b>Already Registered</b>
		</div>
		<table align="center">
			<tr>
				<td class="label">
					User Name :
				</td>
				<td>
					<input type="text" name="user_name" id="usr_name"/>
				</td>
			</tr>
			<tr>
				<td class="label">
					Password :
				</td>
				<td>
					<input type="password" name="password" id="usr_password"/>
				</td>
			</tr>
		</table><br/>
	</div>
	<div id="new_registration" style="display:none;">
	<div class="header">
		<b>New Registration</b>
	</div>
	<table align="center">
		<tr>
			<td class="label">
				User Name :
			</td>
			<td>
				<input type="text" name="name_user" id="name_user"/>
					<b style="color: red;">*</b>
			</td>
		</tr>
		<tr>
			<td class="label">
				Password :
			</td>
			<td>
				<input type="password" name="passwd" id="passwd"/>
				<b style="color: red;">*</b>
			</td>
		</tr>
		<tr>
			<td class="label">
				E-mail :
			</td>
			<td>
				<input type="text" name="email" id="email"/>
				<b style="color: red;">*</b>
			</td>
		</tr>
	</table><br/>
	<div style="text-align: right;">
		<i style="color: red;">* Indicates required fields.</i>
	</div>
	</div>
</div>