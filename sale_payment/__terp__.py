# -*- encoding: utf-8 -*-
{
    "name" : "Sale payment type",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "category" : 'Generic Modules/Sales & Purchases',
    "description": """Adds payment type and bank account to sale process.

The sale order inherits payment type and bank account (if the payment type is related to bank accounts) from partner as default. Next, the invoice based on this sale order inherits the payment information from it.

Also computes payment type and bank account of invoices created from picking lists (extracted from partner info).

Based on previous work of Readylan (version for 4.2).
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
    "active": False,
    "installable": True
}
