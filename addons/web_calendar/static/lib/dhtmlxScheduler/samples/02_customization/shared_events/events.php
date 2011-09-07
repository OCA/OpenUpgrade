<?php
	//connector 1.x
	include ('../../../codebase/connector/scheduler_connector.php');
	include ('../../common/config.php');
	
	$res=mysql_connect($server, $user, $pass);
	mysql_select_db($db_name);
		
	$user_id = intval($_GET['user']);
	
	$scheduler = new schedulerConnector($res);
	$scheduler->enable_log("log.txt",true);
	
	function default_values($action){
		global $user_id;
		
		$event_type = $action->get_value("event_type");
		if ($event_type == "")
			$event_type = 0;
			
		$action->set_value("userId",$user_id);
	}
	$scheduler->event->attach("beforeProcessing","default_values");
	
	$scheduler->render_sql("select * from events_shared where userId = ".$user_id,"event_id","start_date,end_date,text,event_type,userId");
?>