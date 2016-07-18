# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
import logging
from openerp import api, pooler, SUPERUSER_ID
from datetime import datetime


def set_invoice_policy(cr):
    # used to generate the invoice, set it to 'order' which will create the invoice as per ordered quantities.
    openupgrade.logged_query(cr, """
    UPDATE product_template 
    SET invoice_policy = 'order' 
    WHERE invoice_policy IS NULL;
    """)

def set_track_service(cr):
    # Set all records to manual.
    openupgrade.logged_query(cr, """
    UPDATE product_template 
    SET track_service = 'manual' 
    WHERE track_service IS NULL;
    """)

def map_order_state(cr):
    # Mapping values for state field in sale.order and sale.order.line
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('state'), 'state', 
        [('waiting_date', 'sale'), ('progress', 'sale'), ('manual', 'sale'), ('shipping_except', 'sale'), ('invoice_except', 'sale')],
        table='sale_order')

    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('state'), 'state', 
        [('confirmed', 'sale'), ('exception', 'sale')],
        table='sale_order_line')

def product_id_env(env):
    product = env['product.product'].create({'name': 'Service Product', 'type': 'service'})
    env.cr.execute("""UPDATE sale_order_line SET product_id = %s WHERE product_id IS NULL""" % product.id)

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    env = api.Environment(cr, SUPERUSER_ID, {})
    product_id_env(env)
    set_invoice_policy(cr)
    set_track_service(cr)
    map_order_state(cr)
