
<div id=" pond_vote" xmlns:py="http://purl.org/kid/ns#">
	<div class="header">
		<b>Ponderation Suggestion</b>
	</div>
	<form py:if="not error" method="post" name="voting_form" action="/comparison/update_voting">
		<input type="hidden" name="id" value="${id}"/>
		<input type="hidden" id="result" name="res" value="${res}"/>
		<input type="hidden" name="name" value="${name}"/>
		<table id="voting" width="100%">
			<tr>
				<td class="label">
					Factor :
				</td>
				<td>
					<input type="text" style="width: 290px; background: #CCCCCC" name="factor_name" value="${name}" disabled='true'></input>
				</td>
			</tr>
			<tr>
				<td class="label">
					Ponderation :
				</td>
				<td>
					<select style="width: 290px;" name="pond_value" id="pondration">
                        <option py:for="f in count" py:content="f" selected="${tg.selector(f==pond)}"></option>
                    </select>
				</td>
			</tr>
			<tr>
				<td class="label">
					Suggestion :
				</td>
				<td>
					<textarea name="suggestion" cols="35" rows="8"/>
				</td>
			</tr>
		</table>
	</form><br/>
	<div py:if="error" align="right">
		<div class="box2 message">
			${error}
		</div>
	</div>
</div>