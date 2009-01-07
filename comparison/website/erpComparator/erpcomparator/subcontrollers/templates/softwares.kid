<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
    
    <script type="text/javascript">
	    function view_detail(id) {
	    	var elem = document.getElementById(id);
	        elem.style.display = elem.style.display == 'none' ? '' : 'none';
		}
	</script>
    
</head>
<body>
    <div class="mattblacktabs">
		<ul>
	    	<li>
	    		<a href="#" onclick="window.location.href='/comparison'">
	    			<span>Comparison</span>
	    		</a>
	    	</li>
	    	<li id="current">
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
	</div>
	<div class="description" py:for="r in res">
		<table>
			<tr>
				<td>
					<b><u>
						${r['name']} :
					</u></b>
					<span py:if="r['note']" onclick="view_detail('${r['name']}')" style="cursor: pointer;">
						&nbsp;&nbsp;&nbsp;<i>...Description</i>
					</span>
					<span py:if="not r['note']">
						<i>...No Description</i>
					</span>					
				</td>
			</tr>
			<tr>
				<td>
					<div id="${r['name']}" style="display: none; width: 1000px;">${r['note'] or ''}</div>
				</td>
			</tr>
		</table>
	</div>
</body>
</html>