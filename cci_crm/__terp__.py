# -*- encoding: utf-8 -*-
{
    "name" : "CCI CRM",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI CRM",
    "description": """
        - define some groups with access rules
        - so using above rules , new object which will be confidential (can only be accessed by some users of group)
    """,
    "depends" : ["base","crm_configuration","event","cci_partner"],
    "init_xml" : ["cci_crm_data.xml"],
    "demo_xml" : ["cci_crm_demo.xml"],
    "update_xml" : ["cci_crm_view.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

