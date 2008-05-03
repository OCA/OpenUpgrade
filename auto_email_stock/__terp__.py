{
    "name" : "Auto Email Stock Picking",
    "version" : "1.0",
    "depends" : ["smtpclient","stock"],
    "author" : "Tiny",
    "description": """Use Email Client module 
    to Send the Automatic Sales Order to the 
    Customer or supplier by Email 
    when the Picking order confirm
    """,
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules",
    "init_xml" : [
        
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "smtpclient_wizard.xml"
    ],
    "active": False,
    "installable": True
}
