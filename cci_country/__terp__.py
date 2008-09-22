# -*- encoding: utf-8 -*-
{
    "name" : "CCI Country",
    "version" : "1.0",
    "author" : "CCILV",
    "website" : "http://www.ccilv.be",
    "category" : "Generic Modules/CCI Country and Zones Management",
    "description": """
        For some applications in the OpenERP software used by some belgain Chamber of Commerce,
        we need a table regrouping countries and areas (group of countries). The table used by
        defaut in openERP doesn't answer to this need, because it's used in other and we need to
        specify if this code can be used in some cases or others
        This table is by evidence very specific to the Chamber of Commerce dedicated modules
    """,
    "depends" : ["base"],
    "init_xml" : [],
    "demo_xml" : [],

    "update_xml" : ["cci_country_view.xml"],
    "active": False,
    "installable": True
}

