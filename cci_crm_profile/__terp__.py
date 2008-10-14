# -*- encoding: utf-8 -*-
{
    "name" : "CCI CRM Profile",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI CRM Profile",
    "description": """
        specific module for cci project which will use crm_profile module.
    """,
    "depends" : ["base","crm_profiling","base_contact"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["cci_crm_profile_view.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

