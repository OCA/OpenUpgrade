# -*- encoding: utf-8 -*-
{
    "name" : "Point Of Sale Extension",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "category" : "Generic Modules/Sales & Purchases",
    "website": "http://www.zikzakmedia.com",
    "description": """
* Only it allows delete draft or canceled POS orders and POS order lines.
* If POS order has a partner, the partner is stored in:
    - The stock.picking created by the pos order.
    - The account.move.line created by the pos order.
* POS orders with amount_total==0 no creates account moves (it gives error).
* Shows the payment type (journal) in the payments list in teh second tab of the POS.
* The journals used to pay with the POS can be choosed (in the configuration tab of the company: Administration / Users / Companies).
* Product prices with or without taxes included (select in the configuration tab of the company).
* Shows a warning in the payment wizard (but you can continue) if:
    - A product added in the POS order has already been requested by the partner (the partner has a sale order with this product), so the user can decide if is better to do a POS order from a sale order.
    - There is not enough virtual stock in any of the products.
  These two warnings can be activated/desactivated (in the configuration tab of the company).
* List and search POS order lines by number of order, partner and state.
""",
    "depends" : ["point_of_sale"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "company_view.xml",
        "pos_wizard.xml",
        "pos_view.xml",
        "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: