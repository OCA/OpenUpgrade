{
    "name" : "Purchase Number",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com/module_sale.html",
    "depends" : ["purchase","account_base","base_vat"],
    "category" : "Generic Modules/Sales & Purchases",
    "description": """
    Remove the drawback of the purchase numbering, 
    and add new feature that will create number on 
    confirmation of the purchase order
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["purchase_report.xml"],
    "active": False,
    "installable": True
}
