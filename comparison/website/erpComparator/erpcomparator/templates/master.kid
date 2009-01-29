<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
	<meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <meta py:replace="item[:]"/>
    
    <script type="text/javascript" src="/static/javascript/MochiKit/MochiKit.js"></script>
    <script type="text/javascript" src="/static/javascript/master.js"></script>
    <script type="text/javascript" src="/static/javascript/treegrid.js"></script>
    <script type="text/javascript" src="/static/javascript/ajax.js"></script>
    <script type="text/javascript" src="/static/javascript/comparison.js"></script>
    <script type="text/javascript" src="/static/javascript/modalbox.js"></script>
    <script type="text/javascript" src="/static/javascript/swfobject.js"></script>
    
    <link href="/static/css/tabs.css" rel="stylesheet" type="text/css"/>
    <link href="/static/css/treegrid.css" rel="stylesheet" type="text/css"/>
    <link href="/static/css/new_style.css" rel="stylesheet" type="text/css"/>
    <link href="/static/css/modalbox.css" rel="stylesheet" type="text/css"/>

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
    
</head>

<body margin="0" py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">
	<table id="container" border="0" cellpadding="0" cellspacing="0">
    	<tr py:if="value_of('show_header_footer', True)">
        	<td>
				<div id="site">
					<div id="header"></div>
					<div id="header_bar"> 
						<div style="padding: 12px 20px; width: 35%; float: left;">
							Based on<font color="#FF3300"><b> 865 </b></font>
							criterions,<font color="#FF3300"><b> 2000 </b></font>
							user's feedback
						</div>
						<div id="loginbg"> 
					    	<div style="padding-top:5px;padding-left:10px;">
					    			Login : <input type="text" class="textInput"/> 
					    			Password : <input type="text" class="textInput"/>
					      		<button type="button" class="button" name="continue">Continue</button>
					    	</div>
						</div>
					</div>
					
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
						<img src="/static/images/bluebgimage.png"/>
					</div>
					
					<div py:replace="[item.text]+item[:]"></div>
					
					<div align="center" id="bodybackground"><br/>
						(c) 2008-TODAY - Copyright Evaluation-Matrix.com -
						<font color="#990000">
							<a href="mailto:info@evaluation-matrix.com" class ="a">
								Contact us
							</a>
						</font> for more information.
					</div>
					<div>
						<img src="/static/images/footerbg.gif"/>
					</div>
					<div>
						<img src="/static/images/bottom_shadow2.png"/>
					</div>
				</div>
			</td>
		</tr>
	</table>
</body>
</html>
