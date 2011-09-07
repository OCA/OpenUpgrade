<?php
	include ('../../../codebase/connector/scheduler_connector.php');
	include ('../../common/config.php');
	
	$res=mysql_connect($server, $user, $pass);
	mysql_select_db($db_name);
	
	$scheduler = new schedulerConnector($res);
	//$scheduler->enable_log("log.txt",true);
	$scheduler->render_table("events","event_id","start_date,end_date,event_name,details");
?>