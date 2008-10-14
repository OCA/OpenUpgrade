# -*- encoding: utf-8 -*-
{
    "name" : "Payement Term with Cash Discount",
    "version" : "1.0",
    "depends" : ["account",],
    "author" : "Tiny",
    "description" : "",
    "website" : "http://tinyerp.com/",
    "category" : "Generic Modules/Accounting",
    "description": """
    This module adds cash discounts on payment terms. Cash discounts
    for a payment term can be configured with:
        * A number of days,
        * A discount (%),
        * A debit and a credit account
    """,
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "account_cash_discount_view.xml",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

