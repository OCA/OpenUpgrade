# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_field_renames = [
    ("stock.move", "stock_move", "quantity_done", "quantity"),
]

_column_copies = {
    "stock_move_line": [
        ("qty_done", "quantity", None),
    ]
}


def fix_move_line_quantity(env):
    """
    v17 combines what used to be reserved_qty and qty_done.
    We assume that we shouldn't touch an original qty_done on
    done moves, but that we can best reflect the v16 state of
    lines being worked on by adding reserved_qty to the new
    quantity column, which was qty_done in v16

    In post-migration, we'll recompute the quantity field of
    moves affected.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line
        SET quantity = quantity + reserved_qty
        WHERE
        state IN ('assigned', 'partially_available')
        AND reserved_qty <> 0
        """,
    )


def _prefill_sml_quantity_product_uom(env):
    openupgrade.add_columns(
        env,
        [("stock.move.line", "quantity_product_uom", "float", None, "stock_move_line")],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line sml
        SET quantity_product_uom =
        CASE
            WHEN sml.product_uom_id != pt.uom_id
                AND uom_pt.category_id = uom_sml.category_id
            THEN ROUND(
                sml.quantity * uom_pt.factor / uom_sml.factor,
                CASE
                    WHEN uom_pt.rounding = 1.0 THEN 0
                ELSE scale(uom_pt.rounding)
                END
            )
        ELSE sml.quantity
        END
        FROM product_product pp,
            uom_uom uom_sml,
            product_template pt,
            uom_uom uom_pt
        WHERE pp.id = sml.product_id
            AND uom_sml.id = sml.product_uom_id
            AND pt.id = pp.product_tmpl_id
            AND uom_pt.id = pt.uom_id
        """,
    )


def prefill_picked(env):
    """
    Pre-fill picked for stock moves and move lines to reduce ORM
    recomputation during migration.
    """
    openupgrade.add_columns(
        env,
        [
            ("stock.move", "picked", "boolean", True, "stock_move"),
            ("stock.move.line", "picked", "boolean", True, "stock_move_line"),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line sml
        SET picked = FALSE
        FROM stock_move sm
        WHERE sml.move_id = sm.id
          AND sm.state != 'done'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET picked = False
        FROM stock_move sm2
        LEFT JOIN stock_move_line sml
            ON sml.move_id = sm2.id
        WHERE sm.state NOT IN ('done', 'cancel')
            AND sml.id IS NULL
            AND sm.id = sm2.id
        """,
    )
    # Need to set sms picked to False when the related smls are not picked
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET picked=False
        FROM stock_move_line sml
        WHERE sml.move_id = sm.id
          AND NOT sml.picked
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.copy_columns(env.cr, _column_copies)
    fix_move_line_quantity(env)
    _prefill_sml_quantity_product_uom(env)
    prefill_picked(env)
