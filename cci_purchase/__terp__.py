{
    "name" : "CCI Purchase",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI Purchase",
    "description": """
        specific module for cci project which will use purchase module
    """,
    "depends" : ["base","purchase"],
    "init_xml" : [],
    "demo_xml" : [],

    "update_xml" : ["cci_purchase_view.xml","cci_purchase_workflow.xml"],
    "active": False,
    "installable": True
}
