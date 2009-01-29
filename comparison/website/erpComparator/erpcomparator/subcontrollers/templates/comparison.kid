<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
    
</head>
<body>
	<div id="bodybackground">
		<div id="checkboxtext">
			<img style="padding-left: 5px;" src="/static/images/iconarrow.gif" align="absbottom" width="15" height="17"> 
				<span style="font-family: Verdana, Geneva, sans-serif; font-style: normal; font-size: 12px;">
					You can compare among following products :
				</span>
			</img>
		</div>
		<div id="checkboxtext">
			<table name="item_list" id="item_list">
				<tr py:if="selected_items">
					<td py:for="label in titles">
						<input id="${label['id']}" type="checkbox" checked="${tg.selector(label['sel'])}" class="grid-record-selector">${label['name']}</input>
					</td>
				</tr>
				<tr py:if="not selected_items">
					<td py:for="label in titles">
						<input id="${label['id']}" type="checkbox" checked="true" class="grid-record-selector">${label['name']}</input>
					</td>
				</tr>
			</table>
			<img src="/static/images/load.jpg" style="cursor: pointer" onclick="getRecords()"/>
		</div>
    	
	    <div style="padding: 4px; margin: auto; width: 840px;">
			<span id="comparison_tree"/>
			<script type="text/javascript">
	        	var comparison_tree = new TreeGrid('comparison_tree');
	        	
	        	//comparison_tree.options.onbuttonclick = on_button_click;
	        	comparison_tree.setHeaders(${ustr(headers)});
	        	comparison_tree.setRecords('${url}', ${ustr(url_params)});
	        	
	        	comparison_tree.render();
	        </script>
		</div>
	</div>
</body>
</html>




