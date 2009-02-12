
<div id="box" class="new_box" xmlns:py="http://purl.org/kid/ns#">
	<input type="hidden" id="parent_id" name="parent_id" value="${parent_id}"/>
	<input type="hidden" id="ponderation" name="ponderation" value="1.0"/>
	
	<div class="header">
		<b>Propose a New Criterion</b>
	</div>
	
	<table id="voting">
		<tr>
			<td class="label">
				Factor Name :
			</td>
			<td>
				<input type="text" style="width: 290px;" id="factor_id" name="factor_id"/>
				<b style="color: red;">*</b>
			</td>					
		</tr>
		<tr>
			<td class="label">
				Parent Factor :
			</td>
			<td>
				<input type="text" style="width: 290px; background: #CCCCCC" id="parent_name" name="parent_name" value="${parent_name}" disabled='true'/>
			</td>					
		</tr>
		<tr>
			<td class="label">
				Type :
			</td>
			<td>
				<select style="width: 290px;" name="type" id="type">
					<option id="type" selected="true" value=""></option>
                    <option id="view" value="view">Category</option>
                    <option id="criterion" value="criterion" selected="true">Criterion</option>
                </select>
			</td>
		</tr>
	</table><br/>
	<div style="text-align: right;">
		<i style="color: red;">* Indicates required fields.</i>
	</div>
	
	<div py:if="error" id="error_box" align="right">
		<div class="box2 message">
			${error}
		</div>
	</div>
</div>
