# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def merge_priorities(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("priority"),
        "priority",
        [("1", "0"), ("2", "1"), ("3", "1")],
        table="stock_move",
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("priority"),
        "priority",
        [("1", "0"), ("2", "1"), ("3", "1")],
        table="stock_picking",
    )


def recompute_stock_picking_scheduled_date(env):
    env.cr.execute(
        """
        SELECT sp.id
        FROM stock_picking sp
        JOIN stock_move sm ON sm.picking_id = sp.id
        WHERE sm.state NOT IN ('done', 'cancel')"""
    )
    picking_ids = [pick[0] for pick in env.cr.fetchall()]
    if picking_ids:
        pickings = env["stock.picking"].browse(picking_ids)
        pickings._compute_scheduled_date()


def delete_domain_from_view(env):
    view = env.ref("stock.report_stock_quantity_action")
    view.domain = None


@openupgrade.migrate()
def migrate(env, version):
    merge_priorities(env)
    delete_domain_from_view(env)
    openupgrade.load_data(env.cr, "stock", "14.0.1.1/noupdate_changes.xml")
    recompute_stock_picking_scheduled_date(env)
    openupgrade.delete_record_translations(
        env.cr, "stock", ["mail_template_data_delivery_confirmation"]
    )
