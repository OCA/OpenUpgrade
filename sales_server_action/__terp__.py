{
        "name" : "Sales Server Action",
        "version" : "5.0",
        "author" : "Tiny",
        "website" : "http://www.openerp.com",
        "category" : "Vertical Modules/Parametrization",
        "description": """Server Action for Sales Management
You will get 2 actions, for the demonstration for the Server Action
that will helps you to customize the Business process
* One Invoice / Each Sales Order Line
* Two Invoice for One Sales Order
** Invoice for the Stokable products
** Invoice for the Service product
""",
        "depends" : ["sale"],
        "init_xml" : [ ],
        "demo_xml" : [ ],
        "update_xml" : [
            "sale_server_action_data.xml",
            "sale_server_action_condition.xml"
        ],
        "installable": True
} 
