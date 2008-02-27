{
    "name" : "CCI mission",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI mission",
    "description": """
        specific module for cci project.
    """,
    "depends" : ["base",'cci_partner','product'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["cci_mission_view.xml","cci_mission_wizard.xml"],
    "active": False,
    "installable": True
}
