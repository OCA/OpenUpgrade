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

    if(isset($_POST["zids"]))
        $emails = $_POST["zids"];
    else
        $emails = "";
    $emails = explode("|", $emails);
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
    $id = "webmail4";     //define an id
    $GLOBALS["operations"] = new Operations();
    $stores = mapi_getmsgstorestable($session);
    $storeslist = mapi_table_queryallrows($stores);
    $store = mapi_openmsgstore($session, $storeslist[0][PR_ENTRYID]);
    $properties =  $GLOBALS["properties"]->getMailProperties();

    $res="";
    foreach($emails as $email)
        {
        $message = $GLOBALS["operations"]->openMessage($store, hex2bin($email));
        $tmp = $GLOBALS["operations"]->getMessageProps($store, $message, $properties, $html2text = false);
        $res .= "email start\n";
        $res .= "zid:".$tmp[entryid][_content]."\n";
        $res .= "subject:".$tmp[subject]."\n";
        $res .= "from:".$tmp[sender_email_address]."\n";
        $res .= "to:".$tmp[display_to]."\n";
        $res .= "delivery:".$tmp[message_delivery_time][_content]."\n";
        $res .= "body:".$tmp[body]."\n";
        $res .= "email end\n";
        }
    print $res;
?>
