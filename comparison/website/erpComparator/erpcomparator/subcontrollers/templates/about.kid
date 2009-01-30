<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Comparison</title>
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
		    	<a href="#" onclick="window.location.href='/about'">
		    		<img src="/static/images/about_hover.jpg" name="about_image" alt="" border="0" width="173" height="46"/>
		    	</a>
		    </div>
		    <div style="float:left;width:9;">
		    	<img src="/static/images/rightwhitebg.gif" alt="" width="9" height="46"/>
		    </div>          
		</div>
		<div>
			<img src="/static/images/bluebgimage.png"/>
		</div>
	
		<div id="checkboxtext" style="margin: auto; width: 850px; font-family: Verdana, Geneva, sans-serif; font-style: normal; font-size: 12px;">
			<b>Introduction</b><br/>
			
			<p style="text-align: justify;">
				Evaluation-Matrix is a collaborative platform dedicated to evaluate current
				best enterprise management softwares. We focus on a pragmatic approach based
				on reliable and quantifiable criterions.
			</p>
			<p style="text-align: justify;">
				Evaluation-Matrix follows two different objectives:<br/>
				* Building a rated features list reflecting users most common needs and,<br/>
				* Having a way to evaluate available softwares on the market.
			</p>
			<p style="text-align: justify;">
				Our first goal is to precisely define the list of criterions most requested on
				the market. This list is hierarchised based on users most common needs. A
				ponderation is defined on each criterion to reflect the demand on each
				particular feature. The highest the ponderation is, the most requested the
				feature is.
			</p>
			<p style="text-align: justify;">	
				Based on this list of criterions, our second goal is to evaluate the
				functionnal and technical coverage of the most used softwares. This allows
				us to display the result as an evaluation matrix, comparing the different
				solutions.
			</p>
			<p style="text-align: justify;">
				As to maintain and constantly improve the criterions and features list,
				Evaluation-Matrix is based on a collaborative approach. Each user can propose
				new criterions, vote for the pondderation of a criterion or help to evaluate
				a particular software.
			</p>
			
			<b>Methodology</b><br/>
			
			<p style="text-align: justify;">
				Evaluating a software is not an easy task as much of the features are present
				in several softwares in different forms: from the simplest and easiest one to
				the complete but complex ones. As to avoid subjectivness of contributors, we
				decided to base our evaluation criterions based on factual data.
			</p>
			<p style="text-align: justify;">
				For example, we do not try to judge or vote on the quality of a feature because
				it depends too much on the need of a user. So, we perfer computing the quality
				of a feature based on the availability or not of sub-features.
			</p>
			<p style="text-align: justify;">
				<ul><i>Bad criterions :</i>
				<li>Has the software a good multi-warehouse stock management system ? <br/>
					- Adjectives like 'good' are too subjective, you should only focus on the
					  existance or not of some features.</li>
				<li>Does the software has an analytic accounting module ?<br/>
					- This question is not precise. All accouting software have analytic
					  accounting features. So this should be a features with several children
					  criterions to compute the quality of the analytic accounting solution.</li>
				<li>Ability to create a product form ?<br/>
					- This question is not usefull as all software will fit this criterion.</li></ul>
				<ul><i>Good criterions :</i>
				<li>Can you define an unlimitted number of warehouses for stock management ?</li></ul>
			</p>
					
			<b>How to propose a new application ?</b><br/>
			<p style="text-align: justify;">
				We plan to extend the platform to evaluate any kind of enterprise management
				application. From the complete ERP to the smallest application dedicated to a
				very specific need.
			</p>
			<p style="text-align: justify;">
				&lt;Contact us&gt; if you want to suggest new applications to be included in the
				list. Send us a description of the application, the links to the editor website
				and the &lt;following file&gt; where you have completed the second column. Keep empty
				the cells for which you don't know the exact answer.
			</p>
			<p style="text-align: justify;">
				To contact us, send an email to contact@evaluation-matrix.com.
			</p>
			<p style="text-align: justify;">
				<b>NOTE :</b> following file, must be a link to a .csv file with :<br/>
	  			id<br/>
	  			criterion_name<br/>
	  			evaluation (empty column)<br/>
			</p>
	
			<b>About Us</b><br/>
	
			<p style="text-align: justify;">
				Evaluation-Matrix has been made by a group of people sharing the same
				interrests in enterprise management softwares. We often have to compare
				different softwares or find the software that fits best the customer need.
				As to avoid redoing each time the same study or comparisons, we decided to
				setup this platform.
			</p>
			<p style="text-align: justify;">
				In january 2009, we launched evaluation-matrix starting with the current 5 most
				important ERP softwares in the world: SAP, Microsoft Navision, Sage L100, Open
				ERP and Open Bravo.
			</p>
			<p style="text-align: justify;">
				To start with a complete content, we sub-contracted evaluations for the softwares
				we did not had any specific knowledge. It allowed us to launch evaluation-matrix
				with about 800 criterions and the evaluation of these criterions for the
				selected softwares.
			</p>
			<p style="text-align: justify;">
				We plan to extend the evaluation matrix to new applications. Feel free to contact
				us to send us a suggestion.
			</p>
		</div>
	</div>
</body>
</html>