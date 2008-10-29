# -*- encoding: utf-8 -*-
{
    "name" : "CCI EVENT",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI Event",
    "description": """
        specific module for cci project which will use event module from extra addons.
    """,
    "depends" : ["base","event","event_project","account_payment", "membership","cci_account", "cci_partner"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["cci_event_view.xml","cci_event_workflow.xml","cci_event_wizard.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

