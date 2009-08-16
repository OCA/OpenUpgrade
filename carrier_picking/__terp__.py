# -*- encoding: utf-8 -*-
{
    "name" : "Carrier picking",
    "version" : "0.1",
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "category" : "Generic Modules/Others",
    "description": """Carrier picking module:

* Adds contact carrier in picking lists and a field to store additional information (like vehicle's plate) in partner addresses and picking lists""",
    "depends" : ["base","stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "stock_view.xml",
        "partner_view.xml",
    ],
    "active": False,
    "installable": True
}
