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
define('BASE_PATH', dirname($_SERVER['SCRIPT_FILENAME']) . "/");

set_include_path(BASE_PATH."server/" . PATH_SEPARATOR . BASE_PATH."server/PEAR/" .  PATH_SEPARATOR .BASE_PATH. PATH_SEPARATOR ."/usr/share/php/");

require("config.php");
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
require("server/modules/class.maillistmodule.php");

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
    $id = "webmail4";     //define an id
    $GLOBALS["operations"] = new Operations();
    $datas = $GLOBALS["operations"]->getHierarchyList(array(PR_IPM_INBOX));
    $store_idhex = $datas[store][0][attributes][id];
    $entryidhex = $datas[store][0][defaultfolders][inbox];
    $entryid = hex2bin($entryidhex);

    $data = array(
        0 => array(
            "attributes" => array(
                "type" => "list"),
                "store" => $store_idhex,
                "entryid" => $entryidhex,
                "columns" => array(
                    "column" => array(
                        0 => '')
                        ),
                    "restriction" => array(
                        "start" =>""),
                    "data_retrieval" => "normal"));


    $GLOBALS["properties"] = new Properties();
    $email_obj = new MailListModule($id, $data);
    $stores = mapi_getmsgstorestable($session);
    $storeslist = mapi_table_queryallrows($stores);

    $store = mapi_openmsgstore($session, $storeslist[0][PR_ENTRYID]);
    $email_obj->messageList($store, $entryid, $data[0]);
    $result = $GLOBALS["bus"]->getData();
    $result = $result[module][0][action][0][item];

    $res="";
    foreach($result as $email)
        {
        $res .= "email start\n";
        $res .= "zid:".$email[entryid][_content]."\n";
        $res .= "subject:".$email[subject]."\n";
        $res .= "from:".$email[sender_email_address]."\n";
        $res .= "to:".$email[display_to]."\n";
        $res .= "delivery:".$email[message_delivery_time][_content]."\n";
        $res .= "email end\n";
        }
    print $res;
?>
