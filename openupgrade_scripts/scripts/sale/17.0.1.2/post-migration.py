# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Holger Brunn
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _sale_order_populate_locked_field(env):
    """Set state of sale orders in state 'done' to 'sale' and lock them."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order
        SET locked = True, state = 'sale'
        WHERE state = 'done'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "sale", "17.0.1.2/noupdate_changes.xml")
    _sale_order_populate_locked_field(env)
