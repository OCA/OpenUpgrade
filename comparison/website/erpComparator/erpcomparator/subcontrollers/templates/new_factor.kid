
<div id="box" class="new_box" xmlns:py="http://purl.org/kid/ns#">
	<input type="hidden" id="parent_id" name="parent_id" value="${parent_id}"/>
	
	<div class="header">
		<b>Propose New Factor</b>
	</div>
	
	<table id="voting">
		<tr>
			<td class="label">
				Factor Name :
			</td>
			<td>
				<input type="text" style="width: 290px;" id="factor_id" name="factor_id"/>
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
				Ponderation :
			</td>
			<td>
				<select style="width: 290px;" name="ponderation" id="ponderation">
                    <option py:for="f in count" value="${f}">${f}</option>
                </select>
			</td>
		</tr>
		<tr>
			<td class="label">
				Type :
			</td>
			<td>
				<select style="width: 290px;" name="type" id="type">
					<option id="type" selected="true" value=""></option>
                    <option id="view" value="view">View</option>
                    <option id="criterion" value="criterion">Criterion</option>
                </select>
			</td>
		</tr>
	</table>
	
	<div py:if="error" align="right">
		<div class="box2 message">
			${error}
		</div>
	</div>
</div>