<?php
	require_once ('../../../codebase/connector/scheduler_connector.php');
	require_once('../../../codebase/connector/crosslink_connector.php');
	require_once ('../../common/config.php');

	$res=mysql_connect($server, $user, $pass);
	mysql_select_db($db_name);

	$cross = new CrossOptionsConnector($res);
	$cross->options->render_table("user","user_id","user_id(value),username(label)");
	$cross->link->render_table("event_user","event_id", "user_id,event_id");
	
	$fruitCross = new CrossOptionsConnector($res);
	$fruitCross->options->render_table("fruit","fruit_id","fruit_id(value),fruit_name(label)");
	$fruitCross->link->render_table("event_fruit","event_id","fruit_id,event_id");
	
	//sleep(2);
	$scheduler = new SchedulerConnector($res);
	//$scheduler->enable_log("events_log.txt",true);
	
	$scheduler->set_options("user_id", $cross->options);
	$scheduler->set_options("fruit_id", $fruitCross->options);
	
	$scheduler->render_table("events_ms","event_id","start_date,end_date,event_name,details");
?>