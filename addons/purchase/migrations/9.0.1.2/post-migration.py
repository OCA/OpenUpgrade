# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# © 2015 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openerp import api, SUPERUSER_ID


def set_dummy_product(env):
    products = env['product.product'].search([('name', '=', 'Any product')])
    if not products:
        product = env['product.product'].create({
            'name': 'Any product',
            'type': 'service',
            'order_policy': 'manual',
        })
    else:
        product = products[0]

    env.cr.execute(
        """UPDATE purchase_order_line
        SET product_id = %s WHERE product_id IS NULL""",
        (product.id,))


def pricelist_property(cr, env):
    # Created res.currency properties from Purchase Pricelist
    property_rec = env['ir.property'].search(
        [('name', '=', 'property_product_pricelist_purchase'),
         '|',
         ('res_id', 'like', 'res.partner%'),
         ('res_id', '=', False)]
    )
    pricelist = []
    partner = []
    currency = []
    for prop in property_rec:
        if prop.value_reference:
            product_pricelist = prop.value_reference
            res_partner = prop.res_id
            pricelist_id = product_pricelist.split(',')[1]
            pricelist_id = int(pricelist_id)
            currency_rec = env['product.pricelist'].\
                search_read([('id', 'in', [pricelist_id])], ['currency_id'])
            if not currency_rec:
                # Some DB may have incorrect pricelist ids in this
                # property.  It seems that some old bug left ir.properties
                # when pricelists where deleted.
                continue
            currency.append(currency_rec[0]['currency_id'][0])
            pricelist.append(pricelist_id)
            if res_partner:
                partner_id = res_partner.split(',')[1]
                partner_id = int(partner_id)
                partner.append(partner_id)
                cr.execute("""
                insert into ir_property (name, type, company_id, fields_id,
                value_reference, res_id)
                values ('property_purchase_currency_id', 'many2one', 1,
                (select id from ir_model_fields where model = 'res.partner'
                and name = 'property_purchase_currency_id'),
                'res.currency,%(currency)s', 'res.partner,%(partner)s')
                """ % {'currency': currency[-1], 'partner': partner[-1]})
            else:
                cr.execute("""
                insert into ir_property (name, type, company_id, fields_id,
                value_reference)
                values ('property_purchase_currency_id', 'many2one', 1,
                (select id from ir_model_fields where model = 'res.partner'
                and name = 'property_purchase_currency_id'),
                 'res.currency,%(currency)s')
                """ % {'currency': currency[-1]})


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
    set_dummy_product(env)
    pricelist_property(cr, env)
    account_properties(cr)
