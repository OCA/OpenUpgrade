<?php
  	header("Content-type:text/xml");
	ini_set('max_execution_time', 600);
	require_once('../../common/config.php');
	print("<?xml version=\"1.0\"?>");

	$link = mysql_pconnect($server, $user, $pass);
	$db = mysql_select_db ($db_name);

	if (!isset($_GET["pos"])) $_GET["pos"]=0;

	//Create database and table if doesn't exists
		//mysql_create_db($db_name,$link);
		$sql = "Select * from Countries";
	 	$res = mysql_query ($sql);
		if(!$res){
			$sql = "CREATE TABLE Countries (item_id INT UNSIGNED not null AUTO_INCREMENT,item_nm VARCHAR (200),item_cd VARCHAR (15),PRIMARY KEY ( item_id ))";
			$res = mysql_query ($sql);
			populateDBRendom();
		}else{
			
		}
	//populate db with 10000 records
	function populateDBRendom(){
		$filename = getcwd()."./countries.txt";
		$handle = fopen ($filename, "r");
		$contents = fread ($handle, filesize ($filename));
		$arWords = split("\r\n",$contents);
		//print(count($arWords));
		for($i=0;$i<count($arWords);$i++){
			$nm = $arWords[$i];
			$cd = rand(123456,987654);
			$sql = "INsert into Countries(item_nm,item_cd) Values('".$nm."','".$cd."')";
			mysql_query ($sql);
			if($i==9999)
				break;
		}
		fclose ($handle);
	}

	getDataFromDB($_GET["mask"]);
	mysql_close($link);



	//print one level of the tree, based on parent_id
	function getDataFromDB($mask){
		$sql = "SELECT DISTINCT item_nm FROM Countries Where item_nm like '".mysql_real_escape_string($mask)."%'";
		$sql.= " Order By item_nm LIMIT ". $_GET["pos"].",20";

		if ( $_GET["pos"]==0)
			print("<complete>");
		else
			print("<complete add='true'>");
		$res = mysql_query ($sql);
		if($res){
			while($row=mysql_fetch_array($res)){
				print("<option value=\"".$row["item_nm"]."\">");
				print($row["item_nm"]);
				print("</option>");
			}
		}else{
			echo mysql_errno().": ".mysql_error()." at ".__LINE__." line in ".__FILE__." file<br>";
		}
		print("</complete>");
	}
?>
