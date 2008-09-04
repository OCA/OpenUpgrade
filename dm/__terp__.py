# -*- encoding: utf-8 -*-
{
    "name" : "Direct Marketing",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/Direct Marketing",
    "description": """

                    """,
    "depends" : ["project","project_retro_planning"],
    "init_xml" : [ ],
    "demo_xml" : [
                  "campaign_data.xml",
                  ],
    "update_xml" : [
                    "dm_wizard.xml",
                    "dm_security.xml",
                    "offer_view.xml",
                    "offer_step_view.xml",
                    "trademark_view.xml",
                    "campaign_view.xml",
                    "dm_report.xml",
                    "offer_sequence.xml",
                    "dm_data.xml",
                    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

