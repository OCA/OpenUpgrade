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

if(isset($_POST['user']) && isset($_POST["pwd"]) && isset($_POST['start_date']) && isset($_POST['subject']) &&  isset($_POST['description']) && isset($_POST['location']))
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

    ////////////////////
    // data import
    ///////////////////

    //set default value if no data
    if(isset($_POST['zid']))
        $appointment_id = $_POST['zid']; //duration in minutes
    else $appointment_id = "";

    if(isset($_POST['duration']))
        $duration = $_POST['duration']; //duration in minutes
    else $duration = "30";

    if(isset($_POST['reminder']))
        $_POST['reminder']; //in minutes
    else $reminder = "15";

    if(isset($_POST['remind']))
        $remind = $_POST['remind']; //Boolean
    else $remind = "false";

    if(isset($_POST['emails']))
        $emails = $_POST['emails'];
    else $emails = "";

    $start_timestamp = $_POST['start_date'];
    $end_timestamp = strval(intval($start_timestamp) + intval($duration)*60);
    $reminder_timestamp = strval(intval($end_timestamp) - intval($reminder)*60);
    $subject = $_POST['subject'];
    $description = $_POST['description'];
    $location = $_POST['location'];
    $destinataires = explode(";", $emails);

    foreach ($destinataires as $destinataire) {
            $dest[] = array(
                 "name"   => $destinataire,
                 "address"  => $destinataire,
                 "type" => "mapi_to"
                );

    }

    $data = array(
        0 => array(
            "attributes" => array("type" => "save"),
            "store" => $store_idhex,
            "parententryid" => $entryidhex,
            "props" => array(
                "entryid" => $appointment_id,
                "store" => $store_idhex,
                "parent_entryid" => $entryidhex,
                "message_class" => "IPM.Appointment",
                "label" => "0",
                "busystatus" => "2",
                "startdate" => $start_timestamp,
                "commonstart" => $start_timestamp,
                "duedate" => $end_timestamp,
                "commonend" => $end_timestamp,
                "duration" => $duration,
                "alldayevent" => "false",
                "reminder" => $remind,
                "reminder_minutes" => $reminder,
                "reminder_time" => $start_timestamp,
                "flagdueby" =>  $reminder_timestamp,
                "icon_index" => "1024",
                "importance" => "1",
                "sensitivity" => "0",
                "private" => "-1",
                "responsestatus" => "",
                "meetingstatus" => "",
                "recurring" => "false",
                "commonassign" => "l",
                "subject" => $subject,
                "body" => $description,
                "html_body" => $description,
                "location" => $location,
                "toccbcc" => $emails,
                "to" => $emails,
                ),
            "recipients" => array(
                "recipient" => $dest
                ),
                ));

    $GLOBALS["properties"] = new Properties();
    $cont = new AppointmentListModule($id,$data);
    $stores = mapi_getmsgstorestable($session);
    $storeslist = mapi_table_queryallrows($stores);
    $store = mapi_openmsgstore($session, $storeslist[0][PR_ENTRYID]);
    $result =  $cont->save($store,$entryid,$data[0]);
    if(isset($result)) {
    $tmp = $GLOBALS["bus"]->getData();
    $appointment_id = $tmp["module"][0]["action"][0]["item"]["entryid"]["_content"];
    }
    print "result=$result;zid=$appointment_id";
}
?>
