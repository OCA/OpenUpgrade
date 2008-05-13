{
    "name" : "CCI Partner",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI Partner",
    "description": """
        Specific module for cci project which will inherit partner module
    """,
    "depends" : ["base","cci_base_contact"],
    "init_xml" : [],
    "demo_xml" : [ "cci_data.xml", "user_data.xml","zip_data.xml", "courtesy_data.xml","links_data.xml", "activity_data.xml", "states_data.xml", "category_data.xml", "function_data.xml"],

    "update_xml" : ['cci_partner_view.xml','article_sequence.xml','cci_partner_report.xml'],
    "active": False,
    "installable": True,
}
