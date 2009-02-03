
<div id="box" class="new_box" xmlns:py="http://purl.org/kid/ns#">
	<input type="hidden" id="id" name="id" value="${id}"/>
	<input type="hidden" id="item_id" name="item_id" value="${item_id}"/>
	
	<div class="header">
		<b>${item}</b>
	</div>
	
	<table id="voting" align="center">
		<tr style="border: 1px solid #999999">
			<th class="label" style="text-align: left;">Factor Name</th>
			<th class="label" style="text-align: left;">Goodness</th>
		</tr>
		<tr>
			<td colspan="2">
				<hr/>
			</td>
		</tr>
		<tr py:for="ch in child" id="${ch['id']}_row" class="factor_row">
			<td id="${ch['id']}_col" class="factor_col">
				${ch['name']}
			</td>
			<td>
				<select style="width: 150px;" name="${ch['id']}_score_id" id="${ch['id']}_score_id">
					<option name="none" value="0"> </option>				
                	<option py:for="s in value_name" value="${s['id']}">${s['name']}</option>
                </select>
            </td>
        </tr>
	</table><hr/>
	<table align="center">
		<tr>
			<td class="label">
				Note for ${item} :
			</td>
			<td>
				<textarea name="note" id="note" rows="6" cols="25"/>
			</td>
		</tr>
	</table>
		
	<div py:if="error" align="right">
		<div class="box2 message">
			${error}
		</div>
	</div>
</div>