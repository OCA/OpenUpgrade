# -*- encoding: utf-8 -*-
{
    "name" : "Account Payment Extension",
    "version" : "1.1",
    "author" : "Zikzakmedia SL",
    "category" : "Generic Modules/Accounting",
    "website" : "http://www.zikzakmedia.com",
    "description": """Account payment extension.

This module extends the account_payment module with a lot of features:
    * Extension of payment types: The payment type has a translated name and note that can be shown in the invoices.
    * Two default payment types for partners (client and supplier).
    * Automatic selection of payment type in invoices. Now an invoice can have a payment term (30 days, 30/60 days, ...) and a payment type (cash, bank transfer, ...).
    * A default check field in partner bank accounts. The default partner bank accounts are selected in invoices and payments.
    * New menu/tree/forms to see payments to receive and payments to pay.
    * The payments show tree editable fields: Due date, bank account and a check field (for example to write down if a bank check in paper support has been received).
    * Two types of payment orders: Payable payment orders (from supplier invoices) and receivable payment orders (from client invoices). So we can make payment orders to receive the payments of our client invoices. Each payment order type has its own sequence.
    * The payment orders allow negative payment amounts. So we can have payment orders for supplier invoices (pay money) and refund supplier invoices (return or receive money). Or for client invoices (receive money) and refund client invoices (return or pay money).
    * Payment orders: Selected invoices are filtered by payment type, the second message communication can be set at the same time for several invoices.
Based on previous work of Pablo Rocandio & Zikzakmedia (version for 4.2).
""",
    "depends" : [
        "base",
        "account",
        "account_payment",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'security/ir.model.access.csv',
        "payment_wizard.xml",
        "payment_view.xml",
        "payment_sequence.xml",
        ],
    "active": False,
    "installable": True,
}

