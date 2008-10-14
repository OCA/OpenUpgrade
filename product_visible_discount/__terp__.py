# -*- encoding: utf-8 -*-
{
    "name":"Visible Discount Module",
    "version":"1.0",
    "author":"Tiny",
    "category":"Generic Modules/Inventory Control",
    "description": """
    This module use for calculate discount amount on Sale order line and invoice line  base on partner's pricelist
    For that,On the pricelists form, new check box called "Visible Discount" is added.
    Example:
        For product PC1, listprice=450, for partner Asustek, his pricelist calculated is 225 for PC1
        If the check box is ticked, we will have on the SO line (and so also on invoice line): Unit price=450, Discount=50,00, Net price=225
        If the check box is NOT ticked, we will have on SO and Invoice lines: Unit price=225, Discount=0,00, Net price=225

    """,
    "depends":["base","product","account","sale"],
    "demo_xml":[],
    "update_xml":['product_view.xml'],
    "active":False,
    "installable":True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

