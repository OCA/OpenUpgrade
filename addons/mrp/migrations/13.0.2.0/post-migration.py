# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    'mrp.sequence_mrp_unbuild',
]


def convert_many2one_field(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env['stock.move.line'], 'stock_move_line',
        'lot_produced_ids', openupgrade.get_legacy_name('lot_produced_id')
    )


def fill_mrp_unbuild_company_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE mrp_unbuild mu
        SET company_id = ru.company_id
        FROM res_users ru
        WHERE ru.id = mu.create_uid AND mu.company_id IS NULL
        """
    )


def fill_mrp_workorder_product_uom_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE mrp_workorder mw
        SET product_uom_id = mp.product_uom_id
        FROM mrp_production mp
        WHERE mw.production_id = mp.id AND mw.product_uom_id IS NULL
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    convert_many2one_field(env)
    fill_mrp_unbuild_company_id(env.cr)
    fill_mrp_workorder_product_uom_id(env.cr)
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'mrp', 'migrations/13.0.2.0/noupdate_changes.xml')
