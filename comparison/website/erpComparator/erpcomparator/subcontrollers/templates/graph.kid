<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
    
    <script type="text/javascript">
    	MochiKit.DOM.addLoadEvent(function(evt){
    		load_radar();
    	});
	</script>
</head>
<body>
	<div id="bodybackground">
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
		    	<a href="#" onclick="window.location.href='/graph'">
		    		<img src="/static/images/graphs_hover.png" name="graph_image" alt="" border="0" width="175" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left;width:176;">
		    	<a href="#" onclick="window.location.href='/softwares'" onmouseover="document.software_image.src='/static/images/software_hover.jpg'" onmouseout="document.software_image.src='/static/images/software.jpg'">
		    		<img src="/static/images/software.jpg" name="software_image" alt="" border="0" width="176" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left;width:176;">
		    	<a href="#" onclick="window.location.href='/news'" onmouseover="document.news_image.src='/static/images/news_hover.jpg'" onmouseout="document.news_image.src='/static/images/news.jpg'">
		    		<img src="/static/images/news.jpg" name="news_image" alt="" border="0" width="176" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left;width:173;">
		    	<a href="#" onclick="window.location.href='/about'" onmouseover="document.about_image.src='/static/images/about_hover.png'" onmouseout="document.about_image.src='/static/images/about.jpg'">
		    		<img src="/static/images/about.jpg" name="about_image" alt="" border="0" width="173" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left;width:9;">
		    	<img src="/static/images/rightwhitebg.gif" alt="" width="9" height="46"/>
		    </div>          
		</div>
		<div>
			<img src="/static/images/bluebgimage.png"/>
		</div>
		<table id="checkboxtext">
			<tr>
				<td style="font-size: 12px; font-family: Verdana, Geneva, sans-serif; font-style: normal;">
					Analysis axis :
				</td>
				<td>
					<select py:if="view_name" style="width: 500px; font-size: 12px; font-family: Verdana, Geneva, sans-serif; font-style: normal;" name="factors" id="factors" class="factors">
						<option>Summary</option>
			        	<option py:for="s in parents" py:content="s['name']">${s['name']}</option>
			        	<option py:for="c in all_child" selected="${tg.selector(view_name==c['name'])}">${c['name']}</option>
			        </select>
			        <select py:if="not view_name" style="width: 500px; font-size: 12px; font-family: Verdana, Geneva, sans-serif; font-style: normal;" name="factors" id="factors" class="factors">
						<option>Summary</option>
			        	<option py:for="s in parents" py:content="s['name']">${s['name']}</option>
			        	<option py:for="c in all_child" py:content="c['name']">${c['name']}</option>
			        </select>
				</td>
			</tr>
		</table>
		<div id="checkboxtext">
			<table name="item_list" id="graph_item_list">
				<tr py:if="selected_items">
					<td py:for="label in titles">
						<input id="${label['id']}" type="checkbox" checked="${tg.selector(label['sel'])}" class="grid-record-selector">${label['name']}</input>
					</td>
					<td>&nbsp;
						<button type="button" class="button" onclick="load_radar()">Show Graph</button>
					</td>
				</tr>
				<tr py:if="not selected_items">
					<td py:for="label in titles">
						<input id="${label['id']}" type="checkbox" checked="true" class="grid-record-selector">${label['name']}</input>
					</td>
					<td>&nbsp;
						<button type="button" class="button" onclick="load_radar()">Show Graph</button>
					</td>
				</tr>
			</table><br/>
			<table id="checkboxtext">
				<tr>
					<td>
						<div id="radar_chart"></div>
					</td>
				</tr>
			</table>
		</div>
	</div>
</body>
</html>
	