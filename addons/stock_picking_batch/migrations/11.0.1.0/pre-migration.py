# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_table_renames = [
    ('stock_picking_wave', 'stock_picking_batch')
]

_model_renames = [
    ('stock.picking.wave', 'stock.picking.batch')
]

_field_renames = [
    ('stock.picking', 'stock_picking', 'wave_id', 'batch_id'),
]

_xmlid_renames = [
    ('stock_picking_batch.access_stock_picking_wave',
     'stock_picking_batch.access_stock_picking_batch'),
    ('stock_picking_batch.seq_picking_wave',
     'stock_picking_batch.seq_picking_batch'),
    ('stock_picking_batch.menu_action_picking_wave',
     'stock_picking_batch.stock_picking_batch_menu'),
    ('stock_picking_batch.mt_wave_state',
     'stock_picking_batch.mt_batch_state'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_tables(cr, _table_renames)
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(cr, _xmlid_renames)
