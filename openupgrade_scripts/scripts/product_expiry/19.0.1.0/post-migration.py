# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    backfill_stock_move_line_removal_date(env)


def backfill_stock_move_line_removal_date(env):
    """Backfill removal_date on existing move lines - core only creates the
    column empty to avoid a MemoryError on large tables. Mirrors
    _compute_removal_date (lot priority, use_create_lots / use_expiration_date
    gating, picking_id -> move_id fallback for picking type)."""
    env.cr.execute(
        """
        UPDATE stock_move_line sml
        SET removal_date = CASE
            WHEN lot.removal_date IS NOT NULL
            THEN lot.removal_date
            ELSE sml2.expiration_date
                 - (COALESCE(pt.removal_time, 0) || ' days')::interval
        END
        FROM stock_move_line sml2
        JOIN product_product pp ON sml2.product_id = pp.id
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        LEFT JOIN stock_lot lot ON sml2.lot_id = lot.id
        LEFT JOIN stock_picking sp ON sml2.picking_id = sp.id
        LEFT JOIN stock_move sm ON sml2.move_id = sm.id
        LEFT JOIN stock_picking_type spt ON spt.id = COALESCE(
            sp.picking_type_id, sm.picking_type_id
        )
        WHERE sml.id = sml2.id
          AND sml.removal_date IS NULL
          AND (
              lot.removal_date IS NOT NULL
              OR (
                  COALESCE(spt.use_create_lots, FALSE) IS TRUE
                  AND COALESCE(pt.use_expiration_date, FALSE) IS TRUE
                  AND sml2.expiration_date IS NOT NULL
              )
          )
        """
    )
