<?php
file_put_contents("./data.xml",$_POST["data"]);
header("Location:./php/dummy.html");
?>