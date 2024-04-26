# SPDX-FileCopyrightText: 2024 Tecnativa - Pedro M. Baeza
# SPDX-License-Identifier: AGPL-3.0-or-later
import uuid

from openupgradelib import openupgrade


def _assign_pos_order_token(env):
    openupgrade.add_fields(
        env,
        [("access_token", "pos.order", "pos_order", "char", False, "point_of_sale")],
    )
    env.cr.execute("SELECT id FROM pos_order")
    for row in env.cr.fetchall():
        env.cr.execute(
            "UPDATE pos_order SET access_token = %s WHERE id = %s",
            (str(uuid.uuid4()), row[0]),
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(
        env,
        [
            (
                "cash_register_balance_start",
                "pos.session",
                "pos_session",
                "monetary",
                False,
                "point_of_sale",
            )
        ],
    )
    _assign_pos_order_token(env)
