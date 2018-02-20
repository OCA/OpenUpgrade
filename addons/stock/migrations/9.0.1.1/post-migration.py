# -*- coding: utf-8 -*-
# Copyright 2016 - Therp BV
# Copyright 2018 - Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from openerp import SUPERUSER_ID, api
from openupgradelib import openupgrade


def _migrate_tracking(cr):
    # set tracking to lot if tracking is switched on in the first place
    cr.execute(
        "update product_template set tracking='lot' where "
        "track_all or track_incoming or track_outgoing")
    # some of them might be better off as serial tracking, we use lots
    # of size 1 as indicator for that
    cr.execute(
        "with lot_quantities as "
        "(select l.id, l.product_id, sum(qty) sum_qty "
        "from stock_production_lot l "
        "join stock_quant q on q.lot_id=l.id "
        "group by l.id, l.product_id) "
        "update product_template "
        "set tracking='serial' "
        "where id in "
        "(select product_id from lot_quantities lq "
        "where not exists "
        "(select id from lot_quantities "
        "where lot_quantities.product_id=lq.product_id and "
        "lot_quantities.sum_qty<>1))")


def _migrate_pack_operation(env):
    """Create stock.pack.operation.lot records - non existing in v8 -,
    mark pickings that need to recreate pack operations, and update new field
    qty_done on stock.pack.operation for transferred pickings.
    """
    env.cr.execute(
        "select o.id, o.%(lot_id)s, p.state, sum(q.qty) "
        "from stock_pack_operation o "
        "join stock_quant q on q.lot_id=o.%(lot_id)s "
        "join stock_picking p on o.picking_id=p.id "
        "group by o.id, o.%(lot_id)s, p.state",
        {'lot_id': AsIs(openupgrade.get_legacy_name('lot_id'))})
    for operation_id, lot_id, state, qty in env.cr.fetchall():
        env['stock.pack.operation.lot'].create({
            'lot_id': lot_id,
            'operation_id': operation_id,
            'qty': 0 if state not in ['done'] else qty,
            'qty_todo': 0 if state in ['done'] else qty,
        })
    env.cr.execute(
        "update stock_pack_operation "
        "set fresh_record = (%(processed)s = 'false')",
        {'processed': AsIs(openupgrade.get_legacy_name('processed'))})
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_pack_operation spo
        SET qty_done = product_qty
        FROM stock_picking p
        WHERE p.id = spo.picking_id
        AND p.state = 'done'"""
    )


def _migrate_stock_picking(cr):
    cr.execute(
        "update stock_picking p set "
        "location_id=coalesce(location_id, default_location_src_id), "
        "location_dest_id=coalesce(location_dest_id, "
        "default_location_dest_id) "
        "from stock_picking_type t "
        "where p.picking_type_id=t.id and "
        "(location_id is null or location_dest_id is null)")


def _set_lot_params(cr):
    cr.execute(
        "UPDATE stock_picking_type SET use_create_lots = "
        "code = 'incoming'")
    cr.execute(
        "UPDATE stock_picking_type SET use_existing_lots = "
        "code IN ('outgoing', 'internal')")


@openupgrade.migrate()
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _migrate_tracking(cr)
    _migrate_pack_operation(env)
    _migrate_stock_picking(cr)
    _set_lot_params(cr)
