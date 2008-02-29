{
    "name" : "CCI EVENT",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI Event",
    "description": """
        specific module for cci project which will use event module from extra addons.
    """,
    "depends" : ["base","event","account_payment", "membership"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["cci_event_view.xml","cci_event_workflow.xml","cci_event_wizard.xml"],
    "active": False,
    "installable": True
}
