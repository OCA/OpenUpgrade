# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2023 Tecnativa - Pedro M. Baeza
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
        SELECT DISTINCT sp.id
        FROM stock_picking sp
        JOIN stock_move sm ON sm.picking_id = sp.id
        WHERE sp.state NOT IN ('done', 'cancel')"""
    )
    picking_ids = [pick[0] for pick in env.cr.fetchall()]
    if picking_ids:
        pickings = env["stock.picking"].browse(picking_ids)
        pickings._compute_scheduled_date()


def save_stock_picking_date_deadline(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH picking_deadline AS (
            SELECT sp.id,
                CASE
                    WHEN sp.move_type = 'direct' THEN
                        MIN(sm.date_deadline)
                    ELSE
                        MAX(sm.date_deadline)
                END as date_deadline
            FROM stock_picking sp
                JOIN stock_move sm ON sm.picking_id = sp.id
            WHERE sm.date_deadline IS NOT NULL
            GROUP BY sp.id, sp.move_type
        )
        UPDATE stock_picking sp
        SET date_deadline = picking_deadline.date_deadline
        FROM picking_deadline
        WHERE picking_deadline.id = sp.id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_picking sp
        SET has_deadline_issue = TRUE
        WHERE date_deadline IS NOT NULL AND date_deadline < scheduled_date
        """,
    )


def recompute_stock_move_delay_alert_date(env):
    env.cr.execute(
        """
        SELECT sm.id
        FROM stock_move sm
        WHERE sm.state NOT IN ('done', 'cancel')
        """
    )
    move_ids = [move[0] for move in env.cr.fetchall()]
    if move_ids:
        moves = env["stock.move"].browse(move_ids)
        moves._compute_delay_alert_date()


def delete_domain_from_view(env):
    view = env.ref("stock.report_stock_quantity_action")
    view.domain = None


@openupgrade.migrate()
def migrate(env, version):
    merge_priorities(env)
    delete_domain_from_view(env)
    openupgrade.load_data(env.cr, "stock", "14.0.1.1/noupdate_changes.xml")
    recompute_stock_picking_scheduled_date(env)
    save_stock_picking_date_deadline(env)
    recompute_stock_move_delay_alert_date(env)
    openupgrade.delete_record_translations(
        env.cr, "stock", ["mail_template_data_delivery_confirmation"]
    )
