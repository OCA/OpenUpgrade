{
    "name" : "Sale Number",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com/module_sale.html",
    "depends" : ["sale","account_base","base_vat"],
    "category" : "Generic Modules/Sales & Purchases",
    "description": """
    remove the drawback of the sales numbering, 
    and add new feature that will create number on 
    confirmation of the sales order
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["sale_report.xml"],
    "active": False,
    "installable": True
}
