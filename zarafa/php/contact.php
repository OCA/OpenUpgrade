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
require("server/core/class.properties.php");
require("server/modules/class.contactlistmodule.php");

if(isset($_GET['user']) && isset($_GET["pwd"]))
{
//////////////////////////////////
/// get username and password
//////////////////////////////////
$username = $_GET['user'];
$password = $_GET['pwd'];


$server = 'http://localhost:236/zarafa';

//define folder entry and contact entry
$entryidhex =  "00000000b430be451fa24755b247bfdd98686b7c00000000030000007400000000000000";
//$conv = new Conversion();

////////////////////////////////
//connect to the zarafa server
///////////////////////////////
$GLOBALS["mapisession"] = new MAPISession();
$sess = $GLOBALS["mapisession"]->logon($username, $password, $server);
$session = mapi_logon_zarafa($username, $password, $server);


// Create global bus object
$bus = new Bus();
// Make bus global
$GLOBALS["bus"] = $bus;
$GLOBALS["settings"] = new Settings();
$storelist = $GLOBALS["mapisession"]->getAllMessageStores();

//define an id
$id = "webclient_7";

$GLOBALS["operations"] = new Operations();
$datas = $GLOBALS["operations"]->getHierarchyList(array(PR_IPM_CONTACT_ENTRYID));
$store_idhex = $datas[store][0][attributes][id];
$entryidhex = $datas[store][0][defaultfolders][contact];

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
                    "character" => "a",
                    "start" =>"0"),
                "data_retrieval" => "normal"));


$GLOBALS["properties"] = new Properties();
$cont = new ContactListModule($id,$data);

$stores = mapi_getmsgstorestable($session);
$storeslist = mapi_table_queryallrows($stores);

$store = mapi_openmsgstore($session, $storeslist[0][PR_ENTRYID]);
$test = $cont-> messageList($store,$entryid,$data[0]);

$result = $GLOBALS["bus"]->getData();
$result = $result[module][0][action][0][item];
$res = "";
foreach($result as $contact)
    {
    $res .= "contact start\n";
    $res .= "zid:".$contact[entryid][_content]."\n";
    $res .= "name:".$contact[display_name]."\n";
    $res .= "email:".$contact[email_address_1]."\n";
    $res .= "company:".$contact[company_name]."\n";
    $res .= "fax:".$contact[business_fax_number]."\n";
        $res .= "mobile:".$contact[cellular_telephone_number]."\n";
    $res .= "phone:".$contact[office_telephone_number]."\n";
    $res .="contact end\n";
    }

print "$res";

}
?>
