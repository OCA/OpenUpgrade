# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2016 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# © 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openerp import api, SUPERUSER_ID


def set_invoice_policy(env):
    value = env['ir.values'].get_default('sale.order', 'order_policy')
    policy = 'delivery' if value == 'picking' else 'order'
    env['ir.values'].set_default('product.template', 'invoice_policy', policy)
    openupgrade.logged_query(
        env.cr,
        """UPDATE product_template
        SET invoice_policy = %s
        WHERE invoice_policy IS NULL AND type != 'service';""",
        (policy,))
    openupgrade.logged_query(
        env.cr,
        """UPDATE product_template
        SET invoice_policy = 'order'
        WHERE invoice_policy IS NULL""")


def set_track_service(cr):
    """ Set all records to manual """
    openupgrade.logged_query(cr, """
        UPDATE product_template
        SET track_service = 'manual'
        WHERE track_service IS NULL;
    """)


def set_dummy_product(env):
    product = env['product.product'].create({
        'name': 'Any product',
        'type': 'service',
        'order_policy': 'manual',
        'uom_id': env.ref('product.product_uom_unit').id,
    })
    env.cr.execute(
        """UPDATE sale_order_line
        SET product_id = %s WHERE product_id IS NULL""",
        (product.id,))


def set_crm_team_message_types(env):
    """ Add two new default message types to existing subscriptions """
    env['mail.followers'].search([('res_model', '=', 'crm.team')]).write(
        {'subtype_ids': [
            (4, env.ref('sale.mt_salesteam_invoice_confirmed').id),
            (4, env.ref('sale.mt_salesteam_invoice_created').id)]})


@openupgrade.migrate()
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    set_dummy_product(env)
    set_invoice_policy(env)
    set_track_service(cr)
    set_crm_team_message_types(env)
    openupgrade.load_data(
        cr, 'sale', 'migrations/9.0.1.0/noupdate_changes.xml')
