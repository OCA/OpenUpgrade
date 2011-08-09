<?php
	include ('../../../codebase/connector/scheduler_connector.php');
	include ('../../common/config.php');
	
	$res=mysql_connect($server, $user, $pass);
	mysql_select_db($db_name);
	
	$list = new OptionsConnector($res);
	$list->render_table("types","typeid","typeid(value),name(label)");
	
	$scheduler = new schedulerConnector($res);
	//$scheduler->enable_log("log.txt",true);
	
	$scheduler->set_options("type", $list);
	$scheduler->render_table("tevents","event_id","start_date,end_date,event_name,type");
?>