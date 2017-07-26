# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    pl_model = env['product.pricelist']
    sql = """select pricelist_id, website_id, selectable from
          website_pricelist_openupgrade_10"""
    cr.execute(sql)
    pricelists = []
    for pricelist_id, website_id, selectable in cr.fetchall():
        pl_model.search([('id', '=', pricelist_id)]).write({
            'website_id': website_id,
            'selectable': selectable
        })
        pricelists.append(pricelist_id)
    # all remaining pricelists will be assigned to default
    for pricelist in pl_model.search([('id', 'not in', pricelists)]):
        pricelist.write({'website_id': pricelist._default_website().id})
    # now that all pricelists have a their corresponding website_id
    # and selectable drop support table
    sql = "drop table website_pricelist_openupgrade_10"
    cr.execute(sql)
