# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_added_fields = [
    (
        "is_live",
        "payment.transaction",
        "payment_transaction",
        "boolean",
        None,
        "account",
        # we assume all transactions in production system are live
        True,
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _added_fields)
