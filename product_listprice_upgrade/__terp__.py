# -*- encoding: utf-8 -*-
{
    "name":"Product listprice upgrade",
    "version":"1.0",
    "author":"Tiny",
    "category":"Generic Modules/Inventory Control",
    "description": """
    The aim of this module is to allow the automatic upgrade of the field 'List Price' on each product.
    * added a new price type called 'Internal Pricelist' (currently, we have only 2 price types: Sale and Purchase Pricelist)
    * Created a wizard button in the menu Products>Pricelist called 'Upgrade Product List Price'
    * When we have completed the wizard and click on 'Upgrade', it will change the field 'List Price' for all products contained in the categories that we have selected in the wizard
    """,
    "depends":["base","product"],
    "demo_xml":[],
    "update_xml":['product_wizard.xml','product_data.xml'],
    "active":False,
    "installable":True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

