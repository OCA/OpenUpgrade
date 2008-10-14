# -*- encoding: utf-8 -*-
{
    "name" : "Portal Management",
    "version" : "0.1",
    "author" : "Tiny",
    "website" : "http://tinyerp.com/",
    "depends" : ["base"],
    "category" : "Generic Modules/Others",
    "description": """
    Base module to manage portal:
    - define new menu entry with associated actions.
    - add/delete menu entry easily.
    - on-the-fly rules and access control creation.
    """,
    "init_xml" : [],
    "update_xml" : ["portal_conf_data.xml","portal_view.xml","portal_wizard.xml","portal_data.xml"],
    "demo_xml" : ["portal_demo.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

