# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copy = {
    "loyalty_reward": [
        ("reward_type", None, None),
    ],
}


def check_for_free_shipping_promotions(env):
    """
    Since the values of the selection reward_type field only change in the
    sale_loyalty_delivery module, a copy of the column will only be made in case there
    is a free delivery promotion. In case of such a promotion, a copy of the column will
    be made to preserve the data and the relevant data will be modified.
    """
    env.cr.execute(
        """
        SELECT 1 FROM loyalty_reward WHERE reward_type = 'free_shipping'
        """,
    )
    has_free_shipping = env.cr.rowcount
    if has_free_shipping:
        openupgrade.copy_columns(env.cr, _column_copy)
        openupgrade.map_values(
            env.cr,
            openupgrade.get_legacy_name("reward_type"),
            "reward_type",
            [("free_shipping", "shipping")],
            table="loyalty_reward",
        )


@openupgrade.migrate()
def migrate(env, version):
    check_for_free_shipping_promotions(env)
