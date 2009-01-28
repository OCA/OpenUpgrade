<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
    
</head>
<body>
    <div id="site">
		<div style="height: 46px; width: 890px; float: left;">
			<div style="float:left;width:9;">
				<img src="/static/images/whitebg.gif" alt="" width="9" height="46"/>
			</div>
		    <div style="float:left;width:172;">
		    	<a href="#" onclick="window.location.href='/comparison'" onmouseover="document.comparison_image.src='/static/images/comparison_hover.jpg'" onmouseout="document.comparison_image.src='/static/images/comparison.jpg'">
		    		<img src="/static/images/comparison.jpg" name="comparison_image" alt="" border="0" width="172" height="46"/>
		    	</a>
		    </div>
		    
		    <div style="float:left; width:175; height:46;">
		    	<a href="#" onclick="window.location.href='/graph'" onmouseover="document.graph_image.src='/static/images/graphs_hover.jpg'" onmouseout="document.graph_image.src='/static/images/graphs.jpg'">
		    		<img src="/static/images/graphs.jpg" name="graph_image" alt="" border="0" width="175" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left;width:176;">
		    	<a href="#" onclick="window.location.href='/softwares'" onmouseover="document.software_image.src='/static/images/software_hover.jpg'" onmouseout="document.software_image.src='/static/images/software.jpg'">
		    		<img src="/static/images/software.jpg" name="software_image" alt="" border="0" width="176" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left;width:176;">
		    	<a href="#" onclick="window.location.href='/document'" onmouseover="document.document_image.src='/static/images/document_hover.jpg'" onmouseout="document.document_image.src='/static/images/document.jpg'">
		    		<img src="/static/images/document.jpg" name="document_image" alt="" border="0" width="176" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left;width:173;">
		    	<a href="#" onclick="window.location.href='/about'" onmouseover="document.about_image.src='/static/images/about_hover.jpg'" onmouseout="document.about_image.src='/static/images/about.jpg'">
		    		<img src="/static/images/about.jpg" name="about_image" alt="" border="0" width="173" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left;width:9;">
		    	<img src="/static/images/rightwhitebg.gif" alt="" width="9" height="46"/>
		    </div>          
		</div>
		<div>
			<div>
				<img src="/static/images/bluebgimage.png"/>
			</div>
			<div id="checkboxtext">
				<img src="/static/images/iconarrow.gif" align="absbottom" width="15" height="17"/> 
					You can compare among following products :
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
			</div>
			<div id="button">
				<img src="/static/images/reload.jpg" style="cursor: pointer" onclick="getRecords()"/>
			</div><br/>
	    	
		    <div id="open_comp" style="width:890px; overflow-x:scroll">
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
	</div>
</body>
</html>




