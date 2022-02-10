# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'stock_location': [
        ('usage', None, None),
    ],
}

_model_renames = [
    ('report.stock.forecast', 'report.stock.quantity'),
    ('stock.fixed.putaway.strat', 'stock.putaway.rule'),
]

_table_renames = [
    ('stock_fixed_putaway_strat', 'stock_putaway_rule'),
]

_field_renames = [
    ('stock.putaway.rule', 'stock_putaway_rule', 'fixed_location_id', 'location_out_id'),
    ('stock.move', 'stock_move', 'propagate', 'propagate_cancel'),
    ('stock.rule', 'stock_rule', 'propagate', 'propagate_cancel'),
    ('stock.scrap', 'stock_scrap', 'date_expected', 'date_done'),
]

_column_renames = {
    'stock_inventory': [
        ('category_id', None),
        ('filter', None),
        ('location_id', None),
        ('lot_id', None),
        ('package_id', None),
        ('partner_id', None),
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
    # from stock_production_lot_multi_company module
    ('stock.production_lot_comp_rule', 'stock.stock_production_lot_rule'),
]


def assure_stock_rule_company_is_correct(env):
    # avoid company_id check error during update
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_rule sr
        SET company_id = sw.company_id
        FROM stock_warehouse sw
        WHERE sr.warehouse_id = sw.id AND
         (sw.company_id != sr.company_id or sr.company_id IS NULL)"""
    )


def fill_inventory_line_categ(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE stock_inventory_line ADD categ_id int4",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_inventory_line sil
        SET categ_id = pt.categ_id
        FROM product_product pp
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE pp.id = sil.product_id"""
    )


def prefill_stock_picking_type_sequence_code(env):
    """Prefill this field for avoiding the not null warning during update."""
    openupgrade.logged_query(
        env.cr, "ALTER TABLE stock_picking_type ADD sequence_code VARCHAR"
    )
    openupgrade.logged_query(
        env.cr, "UPDATE stock_picking_type SET sequence_code = '-'"
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    if openupgrade.table_exists(env.cr, 'report_stock_quantity'):
        # OCA module `stock_forecast_report` was installed
        # Renaming model and table for not collapsing with the following renames
        openupgrade.rename_models(
            env.cr, [("report.stock.quantity", "report.stock.quantity.ou")]
        )
        openupgrade.rename_tables(
            env.cr, [("report_stock_quantity", "report_stock_quantity_ou")]
        )
        # Remove duplicated access
        env.ref("stock.access_report_stock_quantity").unlink()
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    assure_stock_rule_company_is_correct(env)
    fill_inventory_line_categ(env)
    prefill_stock_picking_type_sequence_code(env)
