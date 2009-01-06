<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
</head>
<body>
	<br/>
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
	    		<a href="#" onclick="window.location.href='/documents'">
	    			<span>Documents</span>
	    		</a>
	    	</li>
	    	<li id="current">
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
	${msg}
</body>
</html>