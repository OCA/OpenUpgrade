# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_fields_renames = [
    ("mrp.workcenter", "mrp_workcenter", "capacity", "default_capacity"),
]
_fields_to_add = [
    ("manual_consumption", "stock.move", "stock_move", "boolean", False, "mrp", False),
]


def _fill_stock_move_manual_consumption(env):
    """Mimic the v15 behavior forcing the manual indication of consumption qtys for
    components with lot/serial number tracking.
    """
    openupgrade.add_fields(env, [_fields_to_add[0]])
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET manual_consumption = True
        FROM product_product pp
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE sm.state = 'draft'
            AND sm.raw_material_production_id IS NOT NULL
            AND pp.id = sm.product_id
            AND pt.tracking <> 'none'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
    _fill_stock_move_manual_consumption(env)
