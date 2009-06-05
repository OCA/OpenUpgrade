<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
    <link href="/static/css/slider.css" rel="stylesheet" type="text/css"/>
    <script type="text/javascript" src="/static/javascript/jq.js"></script>
    <script type="text/javascript" src="/static/javascript/slider.js"></script>

    <script type="text/javascript">
  
    	MochiKit.DOM.addLoadEvent(function(evt){
    		key = true;
    		view_erp_detail('',key,'')
    	});
    
	    function view_detail(id) {
	    	
	    	var elem = document.getElementById(id);
	        elem.style.display = elem.style.display == 'none' ? '' : 'none';
		}
		
		function view_erp_detail(id, key, parent) {
			
			if(key) {
				var table = getElement('checkboxtext');
				id = table.rows[1].id
			}
			
			$(function() {			
				$(".latest_listing_"+id).access({
			        Headline: "Latest Listing",
			        Speed: "normal"
			    });	
			});	
				
			if(key) {
				
				var table = getElement('checkboxtext');
				var tr = table.rows[0];
				var td = MochiKit.DOM.getElementsByTagAndClassName('td', null, tr)[0];
				td.style.color = "#990033";
				table.rows[1].style.display = '';
				var first_init = getElement('img_'+table.rows[1].id) 
				first_init.style.display = '';
			}
			
			else {
			    var p_id = parent.id;
				var ids = p_id.split(',');
					
				for(i in ids)
				{
					if(id == ids[i]) {
						getElement(ids[i]).style.display='';
						getElement('img_'+ids[i]).style.display = '';
						var elem = MochiKit.DOM.getElementsByTagAndClassName('td', null, parent)[i];
						elem.style.color = "#990033";
					}
					else {
						getElement(ids[i]).style.display='none';
						getElement('img_'+ids[i]).style.display = 'none';
						var elem = MochiKit.DOM.getElementsByTagAndClassName('td', null, parent)[i]
						elem.style.color = "#021677";
					}
				}
			}		
		}
		
		
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
		    	<a href="#" onclick="window.location.href='/graph'" onmouseover="document.graph_image.src='/static/images/graphs_hover.png'" onmouseout="document.graph_image.src='/static/images/graphs.jpg'">
		    		<img src="/static/images/graphs.jpg" name="graph_image" alt="" border="0" width="175" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left;width:176;">
		    	<a href="#" onclick="window.location.href='/softwares'">
		    		<img src="/static/images/software_hover.jpg" name="software_image" alt="" border="0" width="176" height="46"/>
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
		<table id="checkboxtext" width="850px" align="center" cellspacing="0">
			<?python
			    id = ''
				for i in range(len(res)):
					if id == '':
						id=str(res[i]['id'])
					else:
						id=id+','+str(res[i]['id'])
			?>
			
			<tr id="${id}" width="100%" class="toolbar">
				<td py:for="r in res" id="'${r['id']}'" onclick="view_erp_detail(${r['id']},false,this.parentNode)" align="center" style="color: #021677; border: 1px solid gray; padding: 2px; white-space:nowrap; font-family: Verdana, Geneva, sans-serif; float: center; width: fixed; cursor: pointer; font-size: 12px;"> 
					<b>
						${r['name']} 
					</b>		
				</td>
			</tr>
			<tr py:for="r in res" id="${r['id']}" style="display:none;">
				<td colspan="${len(res)}">
					<div id="${r['name']}" style="color: #252a28; padding-left: 5px; overflow-y: hidden; overflow-x: auto; width: 830px;">
							<pre py:if="r['note']" py:content="XML(r['note'])">content</pre>
							<pre py:if="not r['note']">No Description...</pre>
					</div>
				</td>
			</tr>
		</table>
		
		<div id="scr_title" style="padding-left: 25px; padding-right: 25px;" >
			<div style="padding:1px; border: 1px solid grey; background-color: #F6F6F6;">
				<b style="padding-left: 15px; color:#021677;">Screen Gallery</b>
			</div>
		</div>
		
		<div id="screenshots" class="checkboxtext">
			<div py:for="r in res" id="${r['id']}">
				<div class="slider latest_listing_${r['id']}" width="850px">
					<div class="messaging" style="display: none;">Please Note: You may have disabled JavaScript and/or CSS.</div>
					<div class="icon_items" id="img_${r['id']}" style="display:none;">
						<a class="prev" href="#"><img height="16" width="16" env="images" title="Previous" alt="Previous" src="/static/images/previous.png" /></a>         
						<a class="next" href="#" style="display:none;"><img height="16" width="16" env="images" title="Next" alt="Next" src="/static/images/next.png" /></a>
						<div class="news_items">
							<a name="skip_to_1"></a>
							<div id="gallery" >
								<div class="container fl"  py:for="key,val in r['code'].items()">
									<div class="item fl" py:for="image in range(len(val[0]))">
										<a href="/static/images/Screenshots/large_screens/${val[0][image]}" target="_blank">
											<img src="/static/images/Screenshots/${val[0][image]}" alt="${val[1][image]}"/>
										</a>
										<div align="center"><b>${val[1][image]}</b></div>
										
									</div>
								</div>
							</div>		
						</div>			
					</div>
				</div>
			</div>
		</div>
	</div>
</body>
</html>
