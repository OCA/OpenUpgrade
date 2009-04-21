<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
	<meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    
    <script type="text/javascript" src="/static/javascript/MochiKit/MochiKit.js"></script>
    <script type="text/javascript" src="/static/javascript/modalbox.js"></script>
    <script type="text/javascript" src="/static/javascript/master.js"></script>
    <script type="text/javascript" src="/static/javascript/treegrid.js"></script>
    <script type="text/javascript" src="/static/javascript/ajax.js"></script>
    <script type="text/javascript" src="/static/javascript/comparison.js"></script>
    <script type="text/javascript" src="/static/javascript/swfobject.js"></script>
    
    <link href="/static/css/tabs.css" rel="stylesheet" type="text/css"/>
    <link href="/static/css/treegrid.css" rel="stylesheet" type="text/css"/>
    <link href="/static/css/new_style.css" rel="stylesheet" type="text/css"/>
    <link href="/static/css/modalbox.css" rel="stylesheet" type="text/css"/>
    <link href="/static/css/planet.css" rel="stylesheet" type="text/css"/>
	<script type="text/javascript">
	   	function lang_change(val) {
			lang_code = val.value;
			
			var get_language = getElement('language');
			lang_code = get_language.value;
			window.location.href=getURL('/comparison', {'lang_code': lang_code});
		}
    </script>
	<meta py:replace="item[:]"/>
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

<?python
# put in try block to prevent improper redirection on connection refuse error
try:
    criterions, feedbacks, user_info = tg.root.comparison.check_data()
except:
	criterions = None
	feedbacks = None
	user_info = None
?>

	<table id="container" border="0" cellpadding="0" cellspacing="0">
    	<tr py:if="value_of('show_header_footer', True)">
        	<td>
				<div id="site">
					<div id="header"></div>
					
					<div id="header_bar"> 
						<table>
							<tr>
								<td style="padding-top:1px; padding-left:10px; width: 30%; float: left;">
									Based on<font color="#FF3300"><b> ${criterions} </b></font>
									criteria,<font color="#FF3300"><b> ${feedbacks} </b></font>
									users' feedbacks
								</td>
									
								<td id="loginbg" py:if="not user_info" style="float: left; width: 65%"> 
							    	<div style="padding-top:5px; padding-left:10px;">
							    			Login : <input type="text" name="user_name" id="user_name" class="textInput"/> 
							    			Password : <input type="password" name="password" id="password" class="textInput"/>
							      		<button type="button" class="button" onclick="do_login()" name="continue">Login</button>
							      		<button type="button" class="button" onclick="register()" name="registration">Registration</button>
							      		<img src="static/images/translate.png" style="padding-left: 5px; padding-top: 0px;"></img>
										<select id="language" onchange="lang_change(this)" style="height: 20px; width: 75px; ">
											<option py:for="lang in rpc.session.lang_data" value="${lang['code']}" selected="${tg.selector(lang['code']==rpc.session.language)}">${lang['name']}</option>
										</select>
							    	</div>
								</td>
								<td id="loginbg" py:if="user_info" width="">
									<table width="100%">
										<tr>
											<td style="align: left; padding-top: 8px; padding-left: 5px; padding-right: 20px; font-size: 12px; font-weight: bold;">
												Welcome ${user_info}
											</td>
											<td style="align: right; padding-top: 6px;">
												<button type="button" style="text-align: right" class="button" onclick="window.location.href='/login/logout'" name="logout">Logout</button>
												<img src="static/images/translate.png"></img>
												<select id="language" onchange="lang_change(this)" style="height: 20px; width: 75px; ">
													<option py:for="lang in rpc.session.lang_data" value="${lang['code']}" selected="${tg.selector(lang['code']==rpc.session.language)}">${lang['name']}</option>
												</select>
											</td>
										</tr>
									</table>
								</td>
								
							</tr>
						</table>						
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
