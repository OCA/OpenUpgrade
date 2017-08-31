# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    pl_model = env['product.pricelist']
    sql = """
    UPDATE product_pricelist pp
    SET website_id = wp.website_id,
        selectable = wp.selectable
        FROM website_pricelist_openupgrade_10 wp
        WHERE wp.pricelist_id = pp.id
    """
    openupgrade.logged_query(cr, sql)
    # all remaining pricelists will be assigned to default
    sql = """select pricelist_id from
          website_pricelist_openupgrade_10"""
    cr.execute(sql)
    pricelist_ids = cr.fetchall()
    for pricelist in pl_model.search([('id', 'not in', pricelist_ids)]):
        pricelist.write({'website_id': pricelist._default_website().id})
    openupgrade.load_data(
        cr, 'website_sale', 'migrations/10.0.1.0/noupdate_changes.xml',
    )
