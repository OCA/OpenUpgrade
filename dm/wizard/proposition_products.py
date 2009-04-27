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
import wizard
import pooler

class wizard_proposition_products(wizard.interface):

    new_prices_prog = '''<?xml version="1.0"?>
    <form string="Select Prices Progression">
        <field name="prices_prog_name"/>
        <field name="fixed_prog"/>
        <field name="percent_prog"/>
    </form>'''

    prices_prog_form = '''<?xml version="1.0"?>
    <form string="">
        <field name="prices_progression" colspan="4"/>
    </form>'''

    message ='''<?xml version="1.0"?>
    <form string="Create Prices Progression">
        <label align="0.0" colspan="4" string="Price Progresson Assigned"/>
    </form>'''

    error_message = '''<?xml version="1.0"?>
    <form string="Error!!!">
        <label align="0.0" colspan="4" string="error test"/>
    </form>'''


    new_prices_prog_fields = {
        'prices_prog_name': {'string': 'Name', 'type': 'char', 'size':64, 'required':True },
        'fixed_prog': {'string': 'Fixed Progression', 'type': 'float', 'digits':(16,2)},
        'percent_prog': {'string': 'Percent Progression Name', 'type': 'float', 'digits':(16,2)},
        }
    
    def _select_prices_prog(self, cr, uid, data, context):
        if context.has_key('prices_prog_id'):
            prices_prog_id = context['prices_prog_id']
        else :
            prices_prog_id = data['form']['prices_progression']

        pool=pooler.get_pool(cr.dbname)
        prop_obj=pool.get('dm.campaign.proposition').browse(cr, uid, data['ids'])[0]
        offer_id=prop_obj.camp_id.offer_id.id
        step_ids=pool.get('dm.offer.step').search(cr, uid, [('offer_id','=',offer_id)])
        step_obj=pool.get('dm.offer.step').browse(cr, uid, step_ids)
        pprog_obj=pool.get('dm.campaign.proposition.prices_progression').browse(cr, uid, prices_prog_id)
        if prop_obj.item_ids:
            for p in prop_obj.item_ids:
                pool.get('dm.campaign.proposition.item').unlink(cr, uid, p.id)

        stp=0

        """Creates proposition items"""
        for step in step_obj:
            for item in step.item_ids:
                if item:
                    if prop_obj.force_sm_price :
                        pu = prop_obj.sm_price
                    else :
                        pu = pool.get('product.pricelist').price_get(cr, uid,
                            [prop_obj.customer_pricelist_id.id], item.id,1.0,
                            context=context)[prop_obj.customer_pricelist_id.id]

                    price = pu * (1 + (stp * pprog_obj.percent_prog)) + (stp * pprog_obj.fixed_prog)
                    vals = {'product_id':item.id,
                            'proposition_id':data['ids'][0],
                            'offer_step_type_id':step.type_id.id,
                            'qty_planned':item.virtual_available,
                            'qty_real':item.qty_available,
                            'price':item.list_price,
                            'notes':item.description,
                            'forecasted_yield' : step.forecasted_yield,
                            }
                    new_id=pool.get('dm.campaign.proposition.item').create(cr, uid, vals)
            stp=stp+1
        """
        pool=pooler.get_pool(cr.dbname)
        prop_obj = pool.get('dm.campaign.proposition')
        for r in prop_obj.browse(cr,uid,data['ids']):
            if not r.campaign_group_id:
                camp_obj.write(cr,uid,r.id,{'campaign_group_id':group_id})
        """
        return {}


    def _new_prices_prog(self, cr, uid, data, context):
        pool=pooler.get_pool(cr.dbname)
        prices_prog_id = pool.get('dm.campaign.proposition.prices_progression').create(cr,uid,{'name':data['form']['prices_prog_name'], 'fixed_prog':data['form']['fixed_prog'], 'percent_prog':data['form']['percent_prog']})
        context['prices_prog_id'] = prices_prog_id
        self._select_prices_prog(cr,uid,data,context)
        return {}

    def _get_prices_progs(self, cr, uid, context):
        pool=pooler.get_pool(cr.dbname)
        prices_prog_obj=pool.get('dm.campaign.proposition.prices_progression')
        ids=prices_prog_obj.search(cr, uid, [])
        res=[(prices_prog.id, prices_prog.name) for prices_prog in prices_prog_obj.browse(cr, uid, ids)]
        res.sort(lambda x,y: cmp(x[1],y[1]))
        return res


    def _next(self, cr, uid, data, context):
        if not data['form']['prices_progression']:
            return 'error'
        return 'select'
    
    def check_price_prog(self, cr, uid, data, context):
        res = pooler.get_pool(cr.dbname).get('dm.campaign.proposition').browse(cr, uid, data['ids'])[0]
        if not res.price_prog_use:
            data['form'] = {'prices_progression': 1}
            return 'select'
        else:
            return 'open'

    prices_prog_fields = {
        'prices_progression': {'string': 'Select Prices Progression', 'type': 'selection', 'selection':_get_prices_progs},
        }


    states = {
        'init': {
            'actions': [],
            'result': {'type':'choice', 'next_state':check_price_prog}
            },
        'open': {
            'actions': [],
            'result': {'type':'form', 'arch':prices_prog_form, 'fields':prices_prog_fields, 'state':[('end','Cancel'),('name_prices_prog','Create New Prices Progression'),('next','Assign Prices Progression'),]}
            },
        'name_prices_prog': {
            'actions': [],
            'result': {'type':'form', 'arch':new_prices_prog, 'fields':new_prices_prog_fields, 'state':[('end','Cancel'),('new','Create Prices Progression')]}
            },
        'new': {
            'actions': [_new_prices_prog],
            'result': {'type': 'form', 'arch': message, 'fields':{} ,'state': [('end', 'Ok', 'gtk-ok', True)]}
        },
        'next': {
            'actions': [],
            'result': {'type': 'choice', 'next_state': _next}
        },
        'error': {
            'actions': [],
            'result': {'type': 'form', 'arch': error_message, 'fields':{} ,'state': [('end','Cancel'),('init','Select Prices Progression')]}
        },
        'select': {
            'actions': [_select_prices_prog],
            'result': {'type': 'form', 'arch': message, 'fields':{} ,'state': [('end', 'Ok', 'gtk-ok', True)]}
        },
        }
wizard_proposition_products("wizard_proposition_products")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
