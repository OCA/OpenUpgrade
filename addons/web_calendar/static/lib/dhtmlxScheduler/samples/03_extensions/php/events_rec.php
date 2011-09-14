<?php
	include ('../../../codebase/connector/scheduler_connector.php');
	include ('../../common/config.php');
	
	$res=mysql_connect($server, $user, $pass);
	mysql_select_db($db_name);
	
	function delete_related($action){
		global $scheduler;
		
		$status = $action->get_status();
		$type =$action->get_value("rec_type");
		$pid =$action->get_value("event_pid");
		//when serie changed or deleted we need to remove all linked events
		if (($status == "deleted" || $status == "updated") && $type!=""){
			$scheduler->sql->query("DELETE FROM events_rec WHERE event_pid='".$scheduler->sql->escape($action->get_id())."'");
		}
		if ($status == "deleted" && $pid !=0){
			$scheduler->sql->query("UPDATE events_rec SET rec_type='none' WHERE event_id='".$scheduler->sql->escape($action->get_id())."'");
			$action->success();
		}
		
	}
	function insert_related($action){
		$status = $action->get_status();
		$type =$action->get_value("rec_type");
		
		if ($status == "inserted" && $type=="none")
			$action->set_status("deleted");
	}
	
	$scheduler = new schedulerConnector($res);
	//$scheduler->enable_log("log.txt",true);
	$scheduler->event->attach("beforeProcessing","delete_related");
	$scheduler->event->attach("afterProcessing","insert_related");
	$scheduler->render_table("events_rec","event_id","start_date,end_date,text,rec_type,event_pid,event_length");
?>