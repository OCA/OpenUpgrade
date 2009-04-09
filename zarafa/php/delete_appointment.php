<?php

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
require("server/modules/class.appointmentitemmodule.php");
require("server/modules/class.appointmentlistmodule.php");

if(isset($_POST['user']) && isset($_POST["pwd"]) && isset($_POST['zid']))
{
    //////////////////////////////////
    /// get username and password
    //////////////////////////////////
    $username = $_POST['user'];
    $password = $_POST['pwd'];
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
    $id = "webclient_7";     //define an id
    $GLOBALS["operations"] = new Operations();
    $datas = $GLOBALS["operations"]->getHierarchyList(array(PR_IPM_APPOINTMENT_ENTRYID));
    $store_idhex = $datas[store][0][attributes][id];
    $entryidhex = $datas[store][0][defaultfolders][calendar];
    $entryid = hex2bin($entryidhex);

    $appointment_id = $_POST['zid'];


    $GLOBALS["properties"] = new Properties();
    $cont = new AppointmentListModule($id,$data);
    $stores = mapi_getmsgstorestable($session);
    $storeslist = mapi_table_queryallrows($stores);
    $store = mapi_openmsgstore($session, $storeslist[0][PR_ENTRYID]);
    $result =  $GLOBALS["operations"]->deleteMessages($store, $entryid, hex2bin($appointment_id));
}
?>
