{
    "name" : "Email Client",
    "version" : "1.0",
    "depends" : ["base","sale"],
    "author" : "Tiny",
    "description": """Email Client module that provides:
    Sending Email
    Use Multiple Server
    Multi Threading
    Multi Attachment
    """,
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules",
    "init_xml" : [
        
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "smtpclient_view.xml",
        "smtpclient_wizard.xml","account_workflow.xml"
    ],
    "active": False,
    "installable": True
}
