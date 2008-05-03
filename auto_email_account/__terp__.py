{
    "name" : "Auto Email Invoice",
    "version" : "1.0",
    "depends" : ["smtpclient","account"],
    "author" : "Tiny",
    "description": """Use Email Client module 
    to Send the Automatic Invoice to the 
    Customer or supplier by Email 
    when the Invoice confirm
    """,
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules",
    "init_xml" : [
        
    ],
    "demo_xml" : [
    ],
    "update_xml" : ["account_invoice_workflow.xml"
        
    ],
    "active": False,
    "installable": True
}
