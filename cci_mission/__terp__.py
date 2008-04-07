{
    "name" : "CCI mission",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI mission",
    "description": """
        specific module for cci project.
    """,
    "depends" : ["base","cci_partner","product","membership", "sale"],
    "init_xml" : [],
    "demo_xml" : ["cci_mission_data.xml"],
    "update_xml" : ["cci_mission_view.xml","cci_mission_wizard.xml","cci_mission_report.xml","cci_mission_workflow.xml" ],
    "active": False,
    "installable": True
}
