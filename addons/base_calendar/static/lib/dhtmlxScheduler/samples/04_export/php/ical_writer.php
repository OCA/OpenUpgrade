<?php
file_put_contents("./data.ical",$_POST["data"]);
header("Location:./php/dummy.html");
?>