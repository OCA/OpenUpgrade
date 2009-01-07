<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
    
    <script type="text/javascript">
	    
	    function selection(id) {
	    	var elem = document.getElementById(id);
	        elem.style.display = '';
		}
		
		function open_comparison(id) {
	    	var elem = document.getElementById(id);
	        elem.style.display = elem.style.display == 'none' ? '' : 'none';
		}
		
		function close_comparison(id) {
	    	var elem = document.getElementById(id);
	        elem.style.display = 'none';
		}
		
	</script>
    
</head>
<body>
    <div class="mattblacktabs">
		<ul>
	    	<li id="current">
	    		<a href="#" onclick="open_comparison('selection'); close_comparison('open_comp');">
	    			<span>Comparison</span>
	    		</a>
	    	</li>
	    	<li>
	    		<a href="#" onclick="window.location.href='/softwares'">
	    			<span>Software</span>
	    		</a>
	    	</li>
	    	<li>
	    		<a href="#" onclick="window.location.href='/documents'">
	    			<span>Documents</span>
	    		</a>
	    	</li>
	    	<li>
	    		<a href="#" onclick="window.location.href='/about'">
	    			<span>About</span>
	    		</a>
	    	</li>
	    	<li>
	    		<a href="#" onclick="window.location.href='/about'">
	    			<span>Graph</span>
	    		</a>
	    	</li>
	  	</ul>
	</div><br/>
	<div id="selection">
		<table>
			<tr>
				<td class="label">
					You can compare among following Products : 
				</td>
				<td py:for="label in titles">
					<input type="checkbox">${label}</input>
				</td>
			</tr>
		</table>
		<br/>
		<button type='button' onclick="close_comparison('selection'); open_comparison('open_comp');">Compare</button>
	</div>
	<div id="open_comp" style="display:none">
		<span id="comparison_tree"/>
		<script type="text/javascript">
        	var comparison_tree = new TreeGrid('comparison_tree');
        	
        	comparison_tree.setHeaders(${ustr(headers)});
        	comparison_tree.setRecords('${url}', ${ustr(url_params)});
        	
        	comparison_tree.render();
        </script>
		
	</div>
</body>
</html>




