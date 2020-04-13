# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    ('report.stock.forecast', 'report.stock.quantity'),
    ('stock.fixed.putaway.strat', 'stock.putaway.rule'),
]

_table_renames = [
    ('stock_fixed_putaway_strat', 'stock_putaway_rule'),
]

_field_renames = [
    ('stock.putaway.rule', 'stock_putaway_rule', 'fixed_location_id', 'location_out_id'),
    ('stock.rule', 'stock_rule', 'propagate', 'propagate_cancel'),
    ('stock.scrap', 'stock_scrap', 'date_expected', 'date_done'),
]

_column_renames = {
    'stock.inventory': [
        ('location_id', None),
        ('product_id', None),
    ],
}

_xmlid_renames = [
    # mail.template
    ('delivery.mail_template_data_delivery_confirmation', 'stock.mail_template_data_delivery_confirmation'),
    # ir.model.access
    ('stock.access_stock_fixed_putaway_strat', 'stock.access_stock_putaway_manager'),
    ('stock.access_stock_fixed_putaway_user', 'stock.access_stock_putaway_all'),
    ('stock.access_stock_forecast_user', 'stock.access_report_stock_quantity'),
    # ir.actions.report
    ('stock_zebra.label_barcode_product_product', 'stock.label_barcode_product_product'),
    ('stock_zebra.label_barcode_product_template', 'stock.label_barcode_product_template'),
    ('stock_zebra.label_lot_template', 'stock.label_lot_template'),
    ('stock_zebra.label_package_template', 'stock.label_package_template'),
    ('stock_zebra.label_picking_type', 'stock.label_picking_type'),
    ('stock_zebra.label_product_packaging', 'stock.label_product_packaging'),
    ('stock_zebra.label_product_product', 'stock.label_product_product'),
    ('stock_zebra.label_product_template', 'stock.label_product_template'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env.cr, _field_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
