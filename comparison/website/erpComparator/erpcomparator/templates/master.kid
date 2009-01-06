<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
	<meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <meta py:replace="item[:]"/>

    <link href="/static/css/style.css" rel="stylesheet" type="text/css"/>
    <link href="/static/css/tabs.css" rel="stylesheet" type="text/css"/>
    <link href="/static/css/treegrid.css" rel="stylesheet" type="text/css"/>

    <!--[if lt IE 7]>
        <link href="/static/css/iepngfix.css" rel="stylesheet" type="text/css"/>
    <![endif]-->

    <!--[if lt IE 7]>
    <style type="text/css">
        ul.tabbernav {
        padding: 0px;
    }

    ul.tabbernav li {
        left: 10px;
        top: 1px;
    }
    </style>
    <![endif]-->

    <!--[if IE]>
        <link href="/static/css/style-ie.css" rel="stylesheet" type="text/css"/>
    <![endif]-->
        
    <title py:replace="''">Your title goes here</title>
    <script type="text/javascript" src="/static/javascript/master.js"></script>
    <script type="text/javascript" src="/static/javascript/treegrid.js"></script>
    <script type="text/javascript" src="/static/javascript/ajax.js"></script>

</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">

	<table id="container" border="0" cellpadding="0" cellspacing="0">
    	<tr>
        	<td class="headerdesign">
				<div class="headerdesign"></div>
				
			</td>
		</tr>		
		<tr>
			<td>
				<div py:replace="[item.text]+item[:]"></div>
			</td>
		</tr>
	</table>
	
</body>
</html>
