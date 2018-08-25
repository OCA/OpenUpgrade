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

import logging
from openerp.openupgrade import openupgrade
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID


logger = logging.getLogger('OpenUpgrade.point_of_sale')


def get_warehouse_id(cr, pool, shop_id):
    """
        Get the sale.shop warehouse_id
    """
    cr.execute(
        "SELECT warehouse_id FROM sale_shop WHERE id=%s", (shop_id,))
    return cr.fetchone()[0]


def get_stock_location_id(cr, pool, shop_id):
    """
        Select the stock_location_id (internal) on pos.config
        to be that of the stock_warehouse of the old shop_id
    """
    wh_obj = pool['stock.warehouse']
    return wh_obj.read(
        cr, SUPERUSER_ID, [get_warehouse_id(cr, pool, shop_id)],
        ['lot_stock_id'])[0]['lot_stock_id'][0]


def get_company_id(cr, pool, shop_id, pc, stock_loc_id):
    """
        Try to get company_id from sale.shop.
        If that fails try to get from the related journal_id
        or the newly added stock_location_id.
        In the end set it to any res.company record.
    """
    cr.execute(
        "SELECT company_id FROM sale_shop WHERE id=%s", (shop_id,))
    comp_id = cr.fetchone()[0]
    if not comp_id:
        comp_obj = pool['res.company']
        comp_id = comp_obj.search(cr, SUPERUSER_ID, [])
        if len(comp_id) > 1:
            if pc.journal_id:
                comp_id = pc.journal_id.company_id.id
            else:
                stock_loc_obj = pool['stock.location']
                stock_loc_comp_id = stock_loc_obj.read(
                    cr, SUPERUSER_ID, [stock_loc_id],
                    ['company_id'])[0]['company_id'][0]
                if stock_loc_comp_id:
                    comp_id = stock_loc_comp_id
                else:
                    comp_id = comp_id[0]
                    comp_name = comp_obj.read(
                        cr, SUPERUSER_ID, [comp_id], ['name'])[0]['name']
                    logger.error(
                        "Could not determine exactly company_id "
                        "for pos.config with (%s, %s). "
                        "Setting it randomly to (%s, %s)."
                        % (pc.id, pc.name, comp_id[0], comp_name))
        else:
            comp_id = comp_id[0]
    return comp_id


def get_pricelist_id(cr, pool, shop_id, pc):
    """
        Get the pricelist_id of the old sale_shop.
    """
    cr.execute(
        "SELECT pricelist_id FROM sale_shop WHERE id=%s", (shop_id,))
    pricelist_id = cr.fetchone()
    if not pricelist_id:
        logger.warning(
            "Could not determine pricelist_id "
            "for pos.config with id=%s (%s)." % (pc.id, pc.name))
        return False
    return pricelist_id[0]


def get_picking_type_id(cr, pool, shop_id, pc, stock_loc_id):
    """
        Create a new picking_type_id using shop info
    """
    pt_obj = pool['stock.picking.type']
    wh = pool['stock.warehouse'].browse(
        cr, SUPERUSER_ID, get_warehouse_id(cr, pool, shop_id))
    return pt_obj.create(cr, SUPERUSER_ID, {
        'name': pc.name,
        'sequence_id': pool['ir.model.data'].xmlid_to_res_id(
            cr, SUPERUSER_ID, 'point_of_sale.seq_picking_type_posout'),
        'code': 'outgoing',
        'warehouse_id': wh.id,
        'default_location_src_id': stock_loc_id,
        'default_location_dest_id': wh.wh_output_stock_loc_id.id,
    })


def migrate_pos_config(cr, pool):
    pc_obj = pool['pos.config']
    pc_ids = pc_obj.search(cr, SUPERUSER_ID, [])
    for pc in pc_obj.browse(cr, SUPERUSER_ID, pc_ids):
        cr.execute("""
            SELECT %s
            FROM pos_config
            WHERE id = %d
        """ % (openupgrade.get_legacy_name('shop_id'), pc.id))
        shop_id = cr.fetchone()[0]
        stock_loc_id = get_stock_location_id(cr, pool, shop_id)
        picking_type_id = get_picking_type_id(
            cr, pool, shop_id, pc, stock_loc_id)
        vals = {
            'stock_location_id': stock_loc_id,
            'company_id': get_company_id(cr, pool, shop_id, pc, stock_loc_id),
            'picking_type_id': picking_type_id,
        }
        pricelist_id = get_pricelist_id(cr, pool, shop_id, pc)
        if pricelist_id:
            vals.update({'pricelist_id': pricelist_id})
        pc.write(vals)
        # Affect all pickings from Pos Order to the new picking_type
        cr.execute("""
            SELECT po.picking_id
            FROM pos_order po
            INNER JOIN pos_session ps on ps.id = po.session_id
            WHERE ps.config_id = %d
            """ % pc.id)
        picking_ids = [x[0] for x in cr.fetchall()]
        if picking_ids:
            openupgrade.logged_query(
                cr, """
                    UPDATE stock_picking
                    SET picking_type_id = %s
                    WHERE id in %s """,
                (picking_type_id, tuple(picking_ids),))


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
        if (
            pc.iface_cashdrawer or pc.iface_payment_terminal or
            pc.iface_electronic_scale or pc.iface_print_via_proxy
        ):
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
    migrate_pos_config(cr, pool)
