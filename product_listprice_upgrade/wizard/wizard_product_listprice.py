# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################



import pooler
import time
import wizard

_pricelist_form = '''<?xml version="1.0"?>
<form string="Upgrade list price">
    <separator string="Select a pricelist " colspan="4"/>
    <field name="pricelist" colspan="4" nolabel="1"/>
    <separator string="Select Product Categories " colspan="4"/>
    <field name="product_category" colspan="4" nolabel="1"/>
    <newline/>
    <field name="upgrade" />
</form>'''

_done_form = '''<?xml version="1.0"?>
<form string="Upgraded list price of prodcuts">
    <field name="update_products"/>

</form>'''

_done_fields = {
    'update_products': {'string':'Upgraded list price of Products', 'type':'float', 'readonly': True},


}

class wizard_product_pricelist(wizard.interface):


    def _get_pricelist(self, cr, uid, context):
        pricelist_obj=pooler.get_pool(cr.dbname).get('product.pricelist')
        ids=pricelist_obj.search(cr, uid, [('type', '=', 'internal'),])
        pricelists=pricelist_obj.browse(cr, uid, ids)
        return [(pricelist.id, pricelist.name ) for pricelist in pricelists]

    def _upgrade_listprice(self, cr, uid, data, context):
        self.update_products=0
        categories_ids=data['form']['product_category']
        pricelist_obj=pooler.get_pool(cr.dbname).get('product.pricelist')
        cat_obj = pooler.get_pool(cr.dbname).get('product.category')
        product_obj = pooler.get_pool(cr.dbname).get('product.product')
        pricelist_id=data['form']['pricelist']

        def _upgrade(category_id):
            if data['form']['upgrade']==True:
                child_ids=cat_obj.search(cr, uid, [('parent_id', '=', category_id),])
                for child_id in child_ids:
                    _upgrade(child_id)
            product_ids=product_obj.search(cr, uid, [('categ_id', '=', category_id),])
            for product_id in product_ids:
                list_price=pricelist_obj.price_get(cr, uid, [pricelist_id], product_id, 1)
                product_obj.write(cr, uid, [product_id], {
                            'list_price': list_price[pricelist_id]})
                self.update_products += 1

        for category_id in categories_ids[0][2]:
            _upgrade(category_id)

        return {'update_products':self.update_products}

    _pricelist_fields = {
        'pricelist': {'string':'Pricelist', 'type':'many2one', 'relation': 'product.pricelist','domain':[('type','=','internal')], 'required':True},
        'product_category': {'string':'Product Category', 'type':'many2many', 'relation': 'product.category', 'required':True},
        'upgrade' : {'string':'Upgrade Child categories', 'type':'boolean', 'default': lambda x,y,z: True}
    }

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':_pricelist_form, 'fields':_pricelist_fields, 'state':[('end','Cancel'),('upgrade','Upgrade')]}
        },
        'upgrade':{
             'actions':[_upgrade_listprice],
             'result':{'type': 'form', 'arch': _done_form, 'fields': _done_fields,'state':[('end', 'End')]}
       }
    }
wizard_product_pricelist('product.listprice')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

