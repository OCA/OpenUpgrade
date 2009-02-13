<?php
session_start();

/*
Zarafa interface (PHP)
(c) 2008 Sednacom
Authors: gael@sednacom.fr

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

*/

 // Include the files

require("config.php");
set_include_path(BASE_PATH."server/" . PATH_SEPARATOR . BASE_PATH."server/PEAR/" .  PATH_SEPARATOR .BASE_PATH. PATH_SEPARATOR ."/usr/share/php/");
require("mapi/mapi.util.php");
require("mapi/mapiguid.php");
require("mapi/mapidefs.php");
require("mapi/mapitags.php");
require("server/util.php");
require("server/core/class.conversion.php");
require("server/core/class.mapisession.php");
require("server/core/class.settings.php");
require("server/core/class.xmlparser.php");
require("server/core/class.bus.php");
require("server/core/class.xmlbuilder.php");
require("server/core/class.operations.php");
require("server/modules/class.module.php");
require("server/modules/class.listmodule.php");
require("server/modules/class.itemmodule.php");
require("server/core/class.properties.php");
require("server/modules/class.createmailitemmodule.php");
require("server/modules/class.maillistmodule.php");

function genere_checknum($taille) {
    $tpass=array();
    $id=0;
    for($i=48;$i<58;$i++) $tpass[$id++]=chr($i);
    for($i=97;$i<123;$i++) $tpass[$id++]=chr($i);
    $checknum="";
    for($i=0;$i<$taille;$i++) {
        $checknum.=$tpass[rand(0,$id-1)];
        }
    return $checknum;
    }


    $checknum = md5(uniqid(rand(),true));
    $_SESSION['files'] = array($checknum => array());

    if($_POST['attachments'] != ""){

        $piece = explode("|",$_POST['attachments']);

        $count = sizeof($piece);
        $cmpt=0;
        $att = array();
        while($cmpt<$count){
            $nom_piece_jointe = $piece[$cmpt];
            $piece_jointe = $piece[$cmpt+1];
            $piece_jointe = base64_decode($piece_jointe);
            // use constant defined by config.php
            $chemin = TMP_PATH.'/';
            $end_file = genere_checknum(6);
            $file = $chemin.$nom_piece_jointe.$end_file;
        $handle_file = fopen($file,"w");
        fwrite($handle_file,$piece_jointe);
        fclose($handle_file);
            // !!! as of Zarafa 6.03, directory name must be stripped !!
            $_SESSION['files'][$checknum][$nom_piece_jointe.$end_file] = array(
                "name" => $nom_piece_jointe,
                "size" => filesize($file),
                "type" => " application/octet-stream",
            );
            $cmpt = $cmpt +2;
        }
    }
    else $attach = "";
    if($_POST['recipients'])
        $ajout_destinataire = true;
    else $ajout_destinataire = false;

    $sujet_mail = $_POST['subject'];
    $body_mail = $_POST['body'];

    $destinataires = explode("|", $_POST['recipients']);
    $to = str_replace('|',';',$_POST['recipients']);
    $dest = array();

    foreach ($destinataires as $destinataire) {
        $dest[] = array(
        "name"   => $destinataire,
        "address"  => $destinataire,
    "type" => "mapi_to"
                );
    }

    //////////////////////////////////
    /// get username and password
    //////////////////////////////////
    $username = $_POST['user'];
    $password = $_POST['password'];
    $server = 'http://localhost:236/zarafa';

   ////////////////////////////////
    //connect to the zarafa server
    ///////////////////////////////
    $GLOBALS["mapisession"] = new MAPISession();
    $sess = $GLOBALS["mapisession"]->logon($username, $password, $server);
    $session = mapi_logon_zarafa($username, $password, $server);
    $bus = new Bus(); // Create global bus object
    $GLOBALS["bus"] = $bus; // Make bus global
    $GLOBALS["settings"] = new Settings();
    $storelist = $GLOBALS["mapisession"]->getAllMessageStores();
    $id = "createmail_".$checknum;     //define an id
    $GLOBALS["operations"] = new Operations();
    $datas = $GLOBALS["operations"]->getHierarchyList(array(PR_IPM_NOTE));
    $store_idhex = $datas[store][0][attributes][id];

    $data = array(
            0 => array(
                "attributes" => array("type" => 'save'),
                "store" => $store_idhex,
                "props" => array(
                                "entryid" => "",
                                "parententry_id" => "",
                                "message_class" => "IPM.Note",
                                "importance" => "1",
                                "use_html" =>"true",
                                "sensitivity" => "0",
                                "read_receipt_requested" => "false",
                                "sent_representing_name" => "",
                                "sent_representing_email_address" => "",
                                "sent_representing_addrtype" => "SMTP",
                                "to" => $to,
                                "cc" => "",
                                "bcc" => "",
                                "subject" => $sujet_mail,
                                "html_body___Config" => "",
                                "dialog_attachments" => $checknum,
                                "html_body" => "",
                                "from" =>"",
                                "body" => $body_mail,
                            ),
                "recipients" => array(
                                "recipient" => $dest
                                ),
                "dialog_attachments" => $checknum,
                "send" => "true",
                )
            );
    $GLOBALS["properties"] = new Properties();
    $email_obj = new CreateMailItemModule($id, $data);
    $send = $email_obj->save('', '', $data[0]);
?>
