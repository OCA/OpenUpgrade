<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
</head>
<body>
	<div id="bodybackground">
		<div style="height: 46px; width: 890px; float: left;">
			<div style="float:left; width:9;">
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
		    <div style="float:left; width:176;">
		    	<a href="#" onclick="window.location.href='/softwares'" onmouseover="document.software_image.src='/static/images/software_hover.jpg'" onmouseout="document.software_image.src='/static/images/software.jpg'">
		    		<img src="/static/images/software.jpg" name="software_image" alt="" border="0" width="176" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left; width:176;">
		    	<a href="#" onclick="window.location.href='/news'" onmouseover="document.news_image.src='/static/images/news_hover.jpg'" onmouseout="document.news_image.src='/static/images/news.jpg'">
		    		<img src="/static/images/news.jpg" name="news_image" alt="" border="0" width="176" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left; width:173;">
		    	<a href="#" onclick="window.location.href='/about'">
		    		<img src="/static/images/about_hover.png" name="about_image" alt="" border="0" width="173" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left; width:9;">
		    	<img src="/static/images/rightwhitebg.gif" alt="" width="9" height="46"/>
		    </div>          
		</div>
		<div>
			<img src="/static/images/bluebgimage.png"/>
		</div>
	
		<div id="checkboxtext" style="margin: auto; width: 850px; font-family: Verdana, Geneva, sans-serif; font-style: normal; font-size: 12px;">
			<b style="color: #021677;">${_("Introduction")}</b><br/>
			
			<p style="text-align: justify; color: #252a28;">
				${_("""Evaluation-Matrix is a collaborative platform dedicated to evaluate current
				best enterprise management softwares. We focus on a pragmatic approach based
				on reliable and quantifiable criteria.""")}
			</p>
			<p style="text-align: justify; color: #252a28;">
				${_("Evaluation-Matrix follows two different objectives:")}<br/>
				${_("* Building a rated features list reflecting users' most common needs and,")}<br/>
				${_("* Having a way to evaluate available softwares on the market.")}
			</p>
			<p style="text-align: justify; color: #252a28;">
				${_("""Our first goal is to precisely define the list of criteria most requested on
				the market. This list is hierarchised based on users' most common needs. A
				ponderation is defined on each criteria to reflect the demand on each
				particular feature. The highest the ponderation is, the most requested the
				feature is.""")}
			</p>
			<p style="text-align: justify; color: #252a28;">	
				${_("""Based on this list of criteria, our second goal is to evaluate the
				functional and technical coverage of the most used softwares. This allows
				us to display the result as an evaluation matrix, comparing the different
				solutions.""")}
			</p>
			<p style="text-align: justify; color: #252a28;">
				${_("""As to maintain and constantly improve the criteria and features list,
				Evaluation-Matrix is based on a collaborative approach. Each user can propose
				new criteria, vote for the ponderation of a criteria or help to evaluate
				a particular software.""")}
			</p>
			
			<b style="color: #021677;">${_("Methodology")}</b><br/>
			
			<p style="text-align: justify; color: #252a28;">
				${_("""Evaluating a software is not an easy task as much of the features are present
				in several softwares in different forms: from the simplest and easiest one to
				the complete but complex ones. As to avoid subjectiveness of contributors, we
				decided to base our evaluation criteria based on factual data.""")}
			</p>
			<p style="text-align: justify; color: #252a28;">
				${_("""For example, we do not try to judge or vote on the quality of a feature because
				it depends too much on the need of a user. So, we perfer to compute the quality
				of a feature based on the availability of sub-features, whether they appear or not.""")}
			</p>
			<p style="text-align: justify;">
				<ul><u><i style="color: #062a1e;">${_("Bad criteria :")}</i></u>
				<li style="color: #252a28;">${_("Does the software have a good multi-warehouse stock management system ?")} <br/>
					${_("""- Adjectives like 'good' are too subjective, you should only focus on the
					  existence of some features whether they exist or not.""")}</li>
				<li style="color: #252a28;">${_("Does the software have an analytic accounting module ?")}<br/>
					${("""- This question is not precise. All accounting softwares have analytic
					  accounting features. So this should be features with several children
					  criteria to compute the quality of the analytic accounting solution.""")}</li>
				<li style="color: #252a28;">${_("Ability to create a product form ?")}<br/>
					${_("- This question is not useful as all softwares will fit this criteria.")}</li></ul>
				<ul><u><i style="color: #062a1e;">${_("Good criteria :")}</i></u>
				<li style="color: #252a28;">${_("Can you define an unlimited number of warehouses for stock management ?")}</li></ul>
			</p>
					
			<!--<b style="color: #021677;">How to propose a new application ?</b><br/>
			<p style="text-align: justify; color: #252a28;">
				We plan to extend the platform to evaluate any kind of enterprise management
				application, from the complete ERP to the smallest application dedicated to a
				very specific need.
			</p>
			<p style="text-align: justify; color: #252a28;">
				&lt;Contact us&gt; if you want to suggest new applications to be included in the
				list. Send us a description of the application, the links to the editor website
				and the &lt;following file&gt; where you have completed the second column. Keep empty
				the cells for which you don't know the exact answer.
			</p>
			<p style="text-align: justify; color: #252a28;">
				To contact us, send an email to  <a href="mailto:info@evaluation-matrix.com" class="a">info@evaluation-matrix.com.
				</a>
			</p>
			<p style="text-align: justify; color: #252a28;">
				<b style="color: #021677;">NOTE :</b> following file, must be a link to a .csv file with :<br/>
	  			id<br/>
	  			criteria_name<br/>
	  			evaluation (empty column)<br/>
			</p>-->
	
			<b style="color: #021677;">${_("About Us")}</b><br/>
	
			<p style="text-align: justify; color: #252a28;">
				${_("""Evaluation-Matrix has been made by a group of people sharing the same
				interests in enterprise management softwares. We often have to compare
				different softwares or to find the software that fits best to the customer need.
				As to avoid redoing each time the same study or comparisons, we decided to
				setup this platform.""")}
			</p>
			<p style="text-align: justify; color: #252a28;">
				${_("""In January 2009, we launched evaluation-matrix starting with the current 5 most
				important ERP softwares in the world: SAP, Microsoft Navision, Sage L100, Open
				ERP and Open Bravo.""")}
			</p>
			<p style="text-align: justify; color: #252a28;">
				${_("""To start with a complete content, we sub-contracted evaluations for the softwares
				we did not have any specific knowledge. It allowed us to launch evaluation-matrix
				with about 950 criteria and the evaluation of these criteria for the
				selected softwares.""")}
			</p>
			<p style="text-align: justify; color: #252a28;">
				${_("""We plan to extend the evaluation matrix to new applications. Feel free to contact
				us to send us a suggestion.""")}
			</p>
		</div>
	</div>
</body>
</html>