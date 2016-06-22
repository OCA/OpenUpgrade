# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
import logging
from openerp import api, pooler, SUPERUSER_ID
from datetime import datetime


def map_order_state(cr):
    # Mapping values of state field for purchase.order
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('state'), 'state', 
        [('approved', 'purchase'), ('bid', 'sent'), 
         ('confirmed', 'to approve'), ('draft', 'draft'),
         ('except_invoice', 'purchase'), ('except_picking', 'purchase')],
        table='purchase_order')

def map_order_line_state(cr):
    cr.execute("""
    UPDATE purchase_order_line l SET state = o.state FROM purchase_order o WHERE l.order_id = o.id
    """)

def product_id_env(env):
    # Assign product where it is NULL
    product = env['product.product'].create({'name': 'Service Product', 
                                             'type': 'service'})
    env.cr.execute("""
        update purchase_order_line set product_id = %s where
        product_id is null""" % product.id)

def pricelist_property(cr, env):
    # Created res.currency properties from Purchase Pricelist 
    property_rec = env['ir.property'].\
        search([('name', '=', 'property_product_pricelist_purchase'),
                '|',('res_id', 'like', 'res.partner%'), ('res_id', '=',
                                                         False)])
    pricelist = []
    partner = []
    currency = []
    for property in property_rec:
        if property.value_reference:
            product_pricelist = property.value_reference
            res_partner = property.res_id
            pricelist_id = product_pricelist.split(',')[1]
            pricelist_id = int(pricelist_id)
            currency_rec = env['product.pricelist'].\
                search_read([('id', 'in', [pricelist_id])], ['currency_id'])
            currency.append(currency_rec[0]['currency_id'][0])
            pricelist.append(pricelist_id)
            if res_partner:
                partner_id = res_partner.split(',')[1]
                partner_id = int(partner_id)
                partner.append(partner_id)
                cr.execute("""
                insert into ir_property (name, type, company_id, fields_id, value_reference, res_id)
                values ('property_purchase_currency_id', 'many2one', 1, (select id from ir_model_fields where model = 'res.partner' and name = 'property_purchase_currency_id'), 'res.currency,%(currency)s', 'res.partner,%(partner)s')
                """ %{'currency' : currency[-1], 'partner' : partner[-1]})
            else:
                cr.execute("""
                insert into ir_property (name, type, company_id, fields_id, value_reference)
                values ('property_purchase_currency_id', 'many2one', 1, (select id from ir_model_fields where model = 'res.partner' and name = 'property_purchase_currency_id'), 'res.currency,%(currency)s')
                """ %{'currency' : currency[-1]})

def account_properties(cr):
    # Handle account properties as their names are changed.
    cr.execute("""
            update ir_property set name = 'property_account_payable_id', 
            fields_id = (select id from ir_model_fields where model 
            = 'res.partner' and name = 'property_account_payable_id') 
            where name = 'property_account_payable' and (res_id like 
            'res.partner%' or res_id is null)
            """)
    cr.execute("""
            update ir_property set fields_id = (select id from 
            ir_model_fields where model = 'res.partner' and 
            name = 'property_account_receivable_id'), name = 
            'property_account_receivable_id' where 
            name = 'property_account_receivable' and (res_id like 
            'res.partner%' or res_id is null)
            """)

@openupgrade.migrate()
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    map_order_state(cr)
    map_order_line_state(cr)
    product_id_env(env)
    pricelist_property(cr, env)
    account_properties(cr)

