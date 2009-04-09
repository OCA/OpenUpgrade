<?php
/* Sincronitzacio TinyERP a Joomla! 1.5 */
/* 20080412 Zikzakmedia SL. www.zikzakmedia.com */
/* Free software under GPL v.3 */

    include("xmlrpc.inc");
    include("xmlrpcs.inc");

    require_once( 'configuration.php' );

        $config = new JConfig;
        $mosConfig_host = $config->host;
        $mosConfig_user = $config->user;
        $mosConfig_password = $config->password;
        $mosConfig_db = $config->db;
        $mosConfig_dbprefix = $config->dbprefix;

    $con = mysql_pconnect($mosConfig_host, $mosConfig_user,$mosConfig_password );
    mysql_select_db($mosConfig_db);

    function debug($s) {
        $fp = fopen("/tmp/debug.xmlrpc.txt","a");
        fwrite($fp, $s."\n");
        fclose($fp);
    }

    function get_table($table, $tiny_data) {
        global $mosConfig_dbprefix;
        $datas=array();

        $qry = "";
        foreach ($tiny_data as $field=>$value)
            $qry .= $field.", ";
        $qry = substr($qry, 0, strlen($qry)-2);

        $result=mysql_query("SELECT ".$qry." FROM ".$mosConfig_dbprefix.$table.";");
        if ($result)
            while ($row=mysql_fetch_row($result)) {
                $data=array(); $cont=0;
                foreach ($tiny_data as $value) {
                    $data[] = new xmlrpcval($row[$cont], $value);
                    $cont++;
                }
                $datas[]=new xmlrpcval($data, "array");
            }
        return new xmlrpcresp( new xmlrpcval($datas, "array"));
    }

    function set_table($table, $tiny_data) {
        global $mosConfig_dbprefix;
        $new = 0;
        $result = mysql_query("SELECT count(*) FROM ".$mosConfig_dbprefix.$table." WHERE id=". $tiny_data['id'] .";");
        $row = mysql_fetch_row($result);
        if (! $row[0] ) {
            $new = 1;
            mysql_query("INSERT INTO ".$mosConfig_dbprefix.$table." (id) VALUES (". $tiny_data['id'] .");");
        }

        // Delete attached files
        $path = "media/".strtr($table,"_","/")."/".$tiny_data['id']; // Directory to store the attached files
        foreach (glob($path."/*") as $file) {
            if (is_file($file)) {
                unlink($file);
            }
        }

        $qry = "";
        foreach ($tiny_data as $field=>$value)
            if (substr($field,0,5) == "fname") { // is an image attached file (fname => full name, picture => image file)
                $filename = $value;
                $extension = strrchr($value,'.');
                $field_picture = "picture".substr($field,5);
                @mkdir($path, 0700, true);
                // Guardem la imatge
                //file_put_contents($filename, base64_decode("media/radiotv/".$table."/".$filename));
                if (!$hd=fopen($path."/".$filename, "wb")) continue;
                fwrite($hd, base64_decode($tiny_data[$field_picture]));
                fclose($hd);
                // Construeix i guarda miniatura de la imatge
                $newxsize=450;
                $newysize=1000;
                $load='imagecreatefrom'.substr($extension,1,strlen($extension)-1);
                $save='image'.substr($extension,1,strlen($extension)-1);
                $tmp_img=$load($path."/".$filename);
                $imgsize = getimagesize($path."/".$filename);
                if ($imgsize[0] > $newxsize || $imgsize[1] > $newysize) {
                    if ($imgsize[0]*$newysize > $imgsize[1]*$newxsize) {
                        $ratio=$imgsize[0]/$newxsize;
                    } else {
                        $ratio=$imgsize[1]/$newysize;
                    }
                } else {
                    $ratio=1;
                }
                //debug($imgsize[0]." ".$imgsize[1]." ".$ratio);
                $tn=imagecreatetruecolor (floor($imgsize[0]/$ratio),floor($imgsize[1]/$ratio));
                imagecopyresized($tn,$tmp_img,0,0,0,0,floor($imgsize[0]/$ratio),floor($imgsize[1]/$ratio),$imgsize[0],$imgsize[1]);
                //$save($tn, $path."/thumb_".$filename);
                if( !is_dir( $path."/thumbs" ) )
                    mkdir( $path."/thumbs",  0777);
                $save($tn, $path."/thumbs/".$filename);

            } elseif (substr($field,0,7) == "picture") { // file of the image attached file. It has been processed in the last if()

            } elseif (substr($field,-4) == "_ids") {
                   $t = explode("_", $table);
                $table1 = $t[1];
                $table2 = substr($field, 0, strlen($field)-4);

                  // If many2many relation: insert in auxiliar table
                // Example of the auxiliar table name: radiotv_channel_program_rel (channel < program) 
                if (strcasecmp($table1, $table2) < 0)
                   $tablerel = $t[0]."_".$table1."_".$table2."_rel";
                else {
                   $tablerel = $t[0]."_".$table2."_".$table1."_rel";
                }
                mysql_query("DELETE FROM ".$mosConfig_dbprefix.$tablerel." WHERE ".$table1."_id = ".$tiny_data['id'].";");
                $qryrel = "INSERT INTO ".$mosConfig_dbprefix.$tablerel." (".$table1."_id, ".$table2."_id) VALUES (".$tiny_data['id'] .",";
                foreach ($value as $v) {
                    mysql_query($qryrel.$v.");");
                    //debug($qryrel.$v.");");
                }

                  // If one2many relation: insert in related table
                mysql_query("UPDATE ".$mosConfig_dbprefix.$t[0]."_".$table2." SET ".$table1."_id=0 WHERE ".$table1."_id=".$tiny_data['id'].";");
                $qryrel = "UPDATE ".$mosConfig_dbprefix.$t[0]."_".$table2." SET ".$table1."_id=".$tiny_data['id']." WHERE id=";
                foreach ($value as $v) {
                    mysql_query($qryrel.$v.";");
                    //debug($qryrel.$v.";");
                }

            } else { // normal field
                $qry .= $field. "='" .addcslashes($value,"'"). "',";
            }

        //debug($qry);
        $result = mysql_query("UPDATE ".$mosConfig_dbprefix.$table." SET ".$qry." changed=1 WHERE id=".$tiny_data['id'].";");
        return new xmlrpcresp(new xmlrpcval($new, "int"));
    }

    function reset_table($table) {
        global $mosConfig_dbprefix;
        mysql_query("UPDATE ".$mosConfig_dbprefix.$table." SET changed=0;");
        return new xmlrpcresp(new xmlrpcval(1, "int"));
    }

    function delete_table($table, $phpfilter) {
        global $mosConfig_dbprefix;
        if ($phpfilter != "") $phpfilter = " AND ".$phpfilter;
        $result = mysql_query("SELECT count(*) FROM ".$mosConfig_dbprefix.$table." WHERE changed=0" .$phpfilter. ";");
        $row = mysql_fetch_row($result);
        $delete = $row[0];
        if ($delete) {
            // Delete attached files
            $result = mysql_query("SELECT id FROM ".$mosConfig_dbprefix.$table." WHERE changed=0" .$phpfilter. ";");
            while ($row = mysql_fetch_array($result)) {
                $path = "media/".strtr($table,"_","/")."/".$row[0]; // Directory to store the attached files
                foreach (glob($path."/*") as $file) {
                    if (is_file($file)) {
                        unlink($file);
                    }
                }
            }
            // Delete records
            mysql_query("DELETE FROM ".$mosConfig_dbprefix.$table." WHERE changed=0" .$phpfilter. ";");
        }
        return new xmlrpcresp(new xmlrpcval($delete, "int"));
    }

    function delete_items($table, $items, $field) {
        // By default $field="id"
        global $mosConfig_dbprefix;
        $delete = 0;
        foreach ($items as $id) {
            // Delete attached files
            $path = "media/".strtr($table,"_","/")."/".$id; // Directory to store the attached files
            foreach (glob($path."/*") as $file) {
                if (is_file($file)) {
                    unlink($file);
                }
            }
            // Delete record
            mysql_query("DELETE FROM ".$mosConfig_dbprefix.$table." WHERE ".$field."=" .$id. ";");
            $delete++;
        }
        return new xmlrpcresp(new xmlrpcval($delete, "int"));
    }

    function get_channel() {
        global $mosConfig_dbprefix;
        $channels=array();

        $result=mysql_query("SELECT name, description FROM ".$mosConfig_dbprefix."radiotv_channel;");
        if ($result) while ($row=mysql_fetch_row($result)) {
            $channels[]=new xmlrpcval(array(new xmlrpcval($row[0], "string"), new xmlrpcval($row[1], "string")), "array");
        }
        return new xmlrpcresp( new xmlrpcval($channels, "array"));
    }

    function set_channel($tiny_data) {
        global $mosConfig_dbprefix;
        $new = 0;

        $result = mysql_query("SELECT count(*) FROM ".$mosConfig_dbprefix."radiotv_channel WHERE id=". $tiny_data['id'] .";");
        $row = mysql_fetch_row($result);
        if (! $row[0] ) {
            $new = 1;
            mysql_query("INSERT INTO ".$mosConfig_dbprefix."radiotv_channel (id) VALUES (". $tiny_data['id'] .");");
        }

        mysql_query("UPDATE ".$mosConfig_dbprefix."radiotv_channel SET ".
            "name='"       .addcslashes($tiny_data['name'],       "'")."',".
            "description='".addcslashes($tiny_data['description'],"'")."',".
            "changed=1 ".
            "WHERE id=".$tiny_data['id'].";");

        return new xmlrpcresp(new xmlrpcval($new, "int"));
    }

    function reset_channel() {
        global $mosConfig_dbprefix;
        mysql_query("UPDATE ".$mosConfig_dbprefix."radiotv_channel SET changed=0;");
        return new xmlrpcresp(new xmlrpcval(1, "int"));
    }

    function delete_channel() {
        global $mosConfig_dbprefix;
        $result = mysql_query("SELECT count(*) FROM ".$mosConfig_dbprefix."radiotv_channel WHERE changed=0;");
        $row = mysql_fetch_row($result);
        $delete = $row[0];
        if ($delete) {
            mysql_query("DELETE FROM ".$mosConfig_dbprefix."radiotv_channel WHERE changed=0;");
        }
        return new xmlrpcresp(new xmlrpcval($delete, "int"));
    }

    function reset_channel_program() {
        global $mosConfig_dbprefix;
        mysql_query("DELETE FROM ".$mosConfig_dbprefix."radiotv_channel_program_rel WHERE 1=1;");
        return new xmlrpcresp(new xmlrpcval(1, "int"));
    }

    $server = new xmlrpc_server( array(
        "get_table" => array(
            "function" => "get_table",
            "signature" => array(array($xmlrpcInt, $xmlrpcString, $xmlrpcStruct))
        ),
        "set_table" => array(
            "function" => "set_table",
            "signature" => array(array($xmlrpcInt, $xmlrpcString, $xmlrpcStruct))
        ),
        "reset_table" => array(
            "function" => "reset_table",
            "signature" => array(array($xmlrpcInt, $xmlrpcString))
        ),
        "delete_table" => array(
            "function" => "delete_table",
            "signature" => array(array($xmlrpcInt, $xmlrpcString, $xmlrpcString))
        ),
        "delete_items" => array(
            "function" => "delete_items",
            "signature" => array(array($xmlrpcInt, $xmlrpcString, $xmlrpcArray, $xmlrpcString))
        ),
        "get_channel" => array(
            "function" => "get_channel",
            "signature" => array(array($xmlrpcArray))
        ),
        "set_channel" => array(
            "function" => "set_channel",
            "signature" => array(array($xmlrpcInt, $xmlrpcStruct))
        ),
        "reset_channel" => array(
            "function" => "reset_channel",
            "signature" => array(array($xmlrpcInt))
        ),
        "delete_channel" => array(
            "function" => "delete_channel",
            "signature" => array(array($xmlrpcInt))
        ),
        "reset_channel_program" => array(
            "function" => "reset_channel_program",
            "signature" => array(array($xmlrpcInt))
        )
    ), false);
    $server->functions_parameters_type= 'phpvals';
    $server->service();
?>
