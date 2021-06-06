# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_empty_discount_policy(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_pricelist
        SET discount_policy = 'with_discount'
        WHERE discount_policy is null
        """,
    )


def copy_date_end_date_start_columns(env):
    openupgrade.copy_columns(
        env.cr,
        {
            "product_pricelist_item": [
                ("date_end", None, None),
                ("date_start", None, None),
            ]
        },
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_empty_discount_policy(env)
    copy_date_end_date_start_columns(env)
