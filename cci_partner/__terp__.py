{
    "name" : "CCI partner",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI Partner",
    "description": """
        specific module for cci project which will inherit partner module
    """,
    "depends" : ["base","cci_base_contact"],
    "init_xml" : [],
    "demo_xml" : ["article_data.xml"],
    "update_xml" : ['cci_partner_view.xml','article_sequence.xml'],
    "active": False,
    "installable": True
}
