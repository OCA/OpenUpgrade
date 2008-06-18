{
    "name" : "Direct Marketing",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/Direct Marketing",
    "description": """
    
                    """,
    "depends" : ["project"],
    "init_xml" : [ ],
    "demo_xml" : ["trademark_data.xml",
                  "campaign_data.xml",
                  "dm_data.xml",
                  ],
    "update_xml" : [
                    "dm_wizard.xml",
                    "offer_view.xml",
					"offer_step_view.xml",
                    "trademark_view.xml",
                    "campaign_view.xml",
                    "dm_report.xml",
                    ],
    "active": False,
    "installable": True
}
