<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
    
    <script type="text/javascript">
    
    	var submit_form = function(form) {
    		form.submit()
    	}
    	
    	addLoadEvent(function(evt){            
            if($('result') &amp;&amp; $('result').value)
                window.close();
        });
    </script>
    
</head>
<body>
	<div class="header">
		<b>Ponderation Suggestion</b>
	</div>
	<form py:if="not error" method="post" name="voting_form" action="/comparison/update_item_voting">
		<input type="hidden" name="id" value="${id}"/>
		<input type="hidden" id="result" name="res" value="${res}"/>
		<input type="hidden" name="item_id" value="${item_id}"/>
		<input type="hidden" name="factor_id" value="${factor_id}"/>
		<table id="voting" width="100%">
			<tr>
				<td class="label">
					Item :
				</td>
				<td>
					<input type="text" style="width: 290px; background: #CCCCCC" name="item_name" value="${item_id}" disabled='true'></input>
				</td>
			</tr>
			<tr>
				<td class="label">
					Factor :
				</td>
				<td>
					<input type="text" style="width: 290px; background: #CCCCCC" name="factor_name" value="${factor_id}" disabled='true'></input>
				</td>
			</tr>
			<tr>
				<td class="label">
					Value :
				</td>
				<td>
					<select style="width: 290px;" name="score_id" id="score_id">
                        <option py:for="s in value_name" py:content="s['name']"></option>
                    </select>
				</td>
			</tr>
			<tr>
				<td class="label">
					Note :
				</td>
				<td>
					<textarea name="note" cols="35" rows="8">
					</textarea>
				</td>
			</tr>
		</table>
		<div class="box2" style="text-align: right;">
			<button type="button" onclick="window.close()">Close</button>
			<button type="button" onclick="submit_form(form)">Save</button>
		</div>
	</form><br/>
	<div py:if="error" align="right">
		<div class="box2 message">
			${error}
		</div>
		<button type="button" onclick="window.close()">Close</button>
	</div>
</body>
</html>