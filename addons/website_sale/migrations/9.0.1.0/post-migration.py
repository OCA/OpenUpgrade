# -*- coding: utf-8 -*-
# © 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openerp import api, SUPERUSER_ID


def set_last_sale_on_partner(env):
    partners = env['res.partner'].search([])
    for partner in partners:
        sale = env['sale.order'].search([
            ('website_order_line', '!=', False),
            ('parner_id', '=', partner.id)
        ], order='date_order desc', limit=1)
        partner.write({'last_website_so_id': sale.id})


@openupgrade.migrate()
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    set_last_sale_on_partner(env)
