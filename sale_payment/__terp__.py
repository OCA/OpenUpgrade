# -*- encoding: utf-8 -*-
{
    "name" : "Sale payment type",
    "version" : "1.0",
    "author" : "Readylan & Zikzakmedia",
    "category" : 'Generic Modules/Sales & Purchases',
    "description": """Adds payment type to sale process.

The sale order inherits payment type from partner as default. Next, the invoice based on this sale order inherits the payment information from it.
""",
    "depends" : [
        "account_payment",
        "account_payment_extension",
        "sale",
        "stock",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "sale_payment_view.xml",
        ],
    "active": True,
    "installable": True
}


