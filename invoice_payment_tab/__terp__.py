{
    "name" : "Invoice payment tab",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/Invoice payment tab",
    "description": """
        - it defines many2many(account.move.line) field on account.invoice
    """,
    "depends" : ["base","account"],
    "init_xml" : [],
    "demo_xml" : [],

    "update_xml" : ["invoice_payment_tab_view.xml"],
    "active": False,
    "installable": True
}
