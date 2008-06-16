{
    "name" : "CCI CRM",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI CRM",
    "description": """
        - define some groups with access rules
        - so using above rules , new object which will be confidential (can only be accessed by some users of grouip)
    """,
    "depends" : ["base","crm"],
    "init_xml" : ["cci_crm_data.xml"],
    "demo_xml" : ["cci_crm_demo.xml"],
    "update_xml" : ["cci_crm_view.xml"],
    "active": False,
    "installable": True
}
