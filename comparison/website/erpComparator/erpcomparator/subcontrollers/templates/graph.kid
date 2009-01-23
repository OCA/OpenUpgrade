<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
</head>
<body>
    <div class="mattblacktabs">
		<ul>
	    	<li>
	    		<a href="#" onclick="window.location.href='/comparison'">
	    			<span>Comparison</span>
	    		</a>
	    	</li>
	    	<li>
	    		<a href="#" onclick="window.location.href='/softwares'">
	    			<span>Software</span>
	    		</a>
	    	</li>
	    	<li>
	    		<a href="#" onclick="window.location.href='/about'">
	    			<span>About</span>
	    		</a>
	    	</li>
	    	<li class="current">
	    		<a href="#" onclick="window.location.href='/graph'">
	    			<span>Graph</span>
	    		</a>
	    	</li>
	    	<li>
	    		<a href="#" onclick="window.location.href='/login'">
	    			<span>Login</span>
	    		</a>
	    	</li>
	    	<li>
	    		<a href="#" onclick="window.location.href='/login/logout'">
	    			<span>Logout</span>
	    		</a>
	    	</li>
	  	</ul>
	</div><br/><br/>
	
	<table>
		<tr>
			<td class="label">
				Analysis axis :
			</td>
			<td>
				<select style="width: 300px;" name="factors" id="factors">				
		        	<option py:for="s in root_factor" py:content="s['name']" selected="${tg.selector(s['name']==selected_fact)}">${s['name']}</option>
		        </select>
			</td>
		</tr>
	</table><br/>
	<table name="item_list" id="graph_item_list">
		<tr>
			<td class="label">
				List of ERP :
			</td>
			<td py:for="label in titles">
				<input id="${label['id']}" type="checkbox" checked="true" class="grid-record-selector">${label['name']}</input>
			</td>
		</tr>
		<tr>
			<td>&nbsp;
			</td>
		</tr>
		<tr>
			<td>
				<button type="button" class="button" onclick="radarData()">Show Graph</button>
			</td>
		</tr>
	</table><br/>	
	<div id="radar_chart"></div>
</body>
</html>
	