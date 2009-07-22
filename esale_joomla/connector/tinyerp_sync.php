<?php

	//defined('_JEXEC') or die('Restricted access');

	include("xmlrpc.inc");
	include("xmlrpcs.inc");
	
	require_once( 'configuration.php' );

	$conn = mysql_connect($host, $user, $password); 
	mysql_select_db($db);	

	
	function getHits($fromDate, $toDate)
	{
		if ( empty($fromDate) && empty($toDate) )
		{
			echo $query = 'SELECT sum(hits) as hit, u.id, u.name FROM jos_content, jos_users as u WHERE u.id = created_by publish_up BETWEEN "'.$fromDate.'" AND "'.$toDate.'" GROUP BY created_by';
		}
		else
		{
			echo $query = 'SELECT sum(hits) as hit, u.id, u.name FROM jos_content, jos_users as u WHERE u.id = created_by  GROUP BY created_by';
		}		
	}


?>