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
                  "campaign_demo.xml",
                  ],
    "update_xml" : [
                    "dm_wizard.xml",
                    "offer_view.xml",
					"offer_step_view.xml",
                    "offer_step_data.xml",
                    "trademark_view.xml",
                    "campaign_view.xml",
                    "campaign_data.xml",
                    "dm_report.xml",
					"dm_data.xml",
                    ],
    "active": False,
    "installable": True
}
