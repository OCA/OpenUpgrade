<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
    <script type="text/javascript" src="/static/javascript/comparison.js"></script>
    
</head>
<body>
	<div class="header">
		<b>Ponderation Suggestion</b>
	</div>
	
	<input type="hidden" name="id" value="${id}"/>
	<input type="hidden" name="item_id" value="${item_id}"/>
	
	<table id="voting" style="width: 800; border: 1px solid #999999;">
		<tr>
			<th class="label" style="text-align: left; border: 1px solid #999999">Factor Name</th>
			<th class="label" style="text-align: left; border: 1px solid #999999">Item</th>
			<th class="label" style="text-align: left; border: 1px solid #999999">Goodness</th>
		</tr>
		<tr py:for="ch in child" id="${ch['id']}_row" class="factor_row">
			<td id="${ch['id']}_col" class="factor_col">
				${ch['name']}
			</td>
			<td>
				<input type="text" style="width: 290px; background: #CCCCCC" id="${ch['id']}_item_name" name="${ch['id']}_item_name" value="${item_id}" disabled='true'></input>			
			</td>
			<td>
				<select style="width: 290px;" name="${ch['id']}_score_id" id="${ch['id']}_score_id">
                    <option py:for="s in value_name" py:content="s['name']"></option>
                </select>
			</td>
		</tr>
	</table>
	
	<div class="box2" style="text-align: right;">
		<button type="button" onclick="window.close()">Close</button>
		<button type="button" onclick="item_vote(${id}, '${item_id}')">Save</button>
	</div><br/>
	
	<div py:if="error" align="right">
		<div class="box2 message">
			${error}
		</div>
		<button type="button" onclick="window.close()">Close</button>
	</div>
</body>
</html>