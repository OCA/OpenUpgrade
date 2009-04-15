{
    "name" : "Google Blogger",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules",
    "description": """
        This module creates wizard in Project Management/Tasks/Export to blog
            - which export user's tasks to blog provided blog id and password in user's form
    """,
    "depends" : ["project"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ['google_blogger_view.xml',
                    'google_blogger_wizard.xml'],
    "active": False,
    "installable": True,
}