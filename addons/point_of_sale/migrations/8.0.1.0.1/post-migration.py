# -*- encoding: utf-8 -*-
##############################################################################
#
#    'Point Of Sale' migration module for Odoo
#    copyright: 2014-Today GRAP
#    @author: Sylvain LE GAL <https://twitter.com/legalsylvain>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.openupgrade import openupgrade
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID


def set_stock_location_id(cr, pool):
    """
        Select the stock_location_id (internal) on pos.config
        to be that of the stock_warehouse of the old shop_id
    """
    pc_obj = pool['pos.config']
    wh_obj = pool['stock.warehouse']
    pc_ids = pc_obj.search(cr, SUPERUSER_ID, [])
    for pc in pc_obj.browse(cr, SUPERUSER_ID, pc_ids):
        cr.execute("""
            SELECT %s
            FROM pos_config
            WHERE id = %d
        """ % (openupgrade.get_legacy_name('shop_id'), pc.id))
        shop_id = cr.fetchone()[0]
        cr.execute(
            "SELECT warehouse_id FROM sale_shop WHERE id=%s", (shop_id,))
        wh_id = cr.fetchone()[0]
        pc.write({
            'stock_location_id': wh_obj.read(
                cr, SUPERUSER_ID, [wh_id],
                ['lot_stock_id'])[0]['lot_stock_id'][0]
        })


def available_in_pos_field_func(cr, pool, id, vals):
    logger.warning(
        'available_in_pos of product.template %d has been set to True '
        'whereas at least one of its product_product was False', id)
    return any(vals)


def expense_pdt_field_func(cr, pool, id, vals):
    logger.warning(
        'expense_pdt of product.template %d has been set to True '
        'whereas at least one of its product_product was False', id)
    return any(vals)


def income_pdt_field_func(cr, pool, id, vals):
    logger.warning(
        'income_pdt of product.template %d has been set to True '
        'whereas at least one of its product_product was False', id)
    return any(vals)


def to_weight_field_func(cr, pool, id, vals):
    logger.warning(
        'to_weight of product.template %d has been set to True '
        'whereas at least one of its product_product was False', id)
    return any(vals)


def set_proxy_ip(cr, pool):
    pc_obj = pool['pos.config']
    pc_ids = pc_obj.search(cr, SUPERUSER_ID, [])
    for pc in pc_obj.browse(cr, SUPERUSER_ID, pc_ids):
        if pc.iface_cashdrawer or pc.iface_payment_terminal \
            or pc.iface_electronic_scale or pc.iface_print_via_proxy:
            pc.write({'proxy_ip': 'http://localhost:8069'})


@openupgrade.migrate()
def migrate(cr, version):
    pool = RegistryManager.get(cr.dbname)
    openupgrade.move_field_m2o(
        cr, pool,
        'product.product', openupgrade.get_legacy_name('available_in_pos'),
        'product_tmpl_id', 'product.template', 'available_in_pos',
        compute_func=available_in_pos_field_func)
    openupgrade.move_field_m2o(
        cr, pool,
        'product.product', openupgrade.get_legacy_name('expense_pdt'),
        'product_tmpl_id', 'product.template', 'expense_pdt',
        compute_func=expense_pdt_field_func)
    openupgrade.move_field_m2o(
        cr, pool, 'product.product', openupgrade.get_legacy_name('income_pdt'),
        'product_tmpl_id', 'product.template', 'income_pdt',
        compute_func=income_pdt_field_func)
    openupgrade.move_field_m2o(
        cr, pool,
        'product.product', openupgrade.get_legacy_name('pos_categ_id'),
        'product_tmpl_id', 'product.template', 'pos_categ_id')
    openupgrade.move_field_m2o(
        cr, pool, 'product.product', openupgrade.get_legacy_name('to_weight'),
        'product_tmpl_id', 'product.template', 'to_weight',
        compute_func=to_weight_field_func)
    set_proxy_ip(cr, pool)
    set_stock_location_id(cr, pool)
