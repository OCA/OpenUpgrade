# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # ir.property
    'stock.property_stock_inventory',
    'stock.property_stock_production',
    # ir.sequence
    'stock.sequence_stock_scrap',
    # stock.location
    'stock.location_inventory',
    'stock.location_procurement',
    'stock.location_production',
    'stock.stock_location_scrapped',
]


def fill_company_id(cr):
    table_list = [
        'stock_putaway_rule',
        'stock_package_level',
        'stock_move_line',
        'stock_picking_type',
        'stock_production_lot',
        'stock_scrap',
    ]
    for table in table_list:
        openupgrade.logged_query(
            cr, """
            UPDATE {table} tbl
            SET company_id = ru.company_id
            FROM res_users ru
            WHERE ru.id = tbl.create_uid AND tbl.company_id IS NULL
            """.format(table=table))


def convert_many2one_field(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env['stock.inventory'], 'stock_inventory',
        'location_ids', openupgrade.get_legacy_name('location_id')
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env['stock.inventory'], 'stock_inventory',
        'product_ids', openupgrade.get_legacy_name('product_id')
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_company_id(env.cr)
    convert_many2one_field(env)
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'stock', 'migrations/13.0.1.1/noupdate_changes.xml')
