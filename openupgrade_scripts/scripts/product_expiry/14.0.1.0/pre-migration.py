# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_field_renames = [
    ("product.template", "product_template", "life_time", "expiration_time"),
    ("stock.production.lot", "stock_production_lot", "life_date", "expiration_date"),
]
_field_creates = [
    (
        "expiration_date",
        "stock.move.line",
        "stock_move_line",
        "datetime",
        False,
        "stock",
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.add_fields(env, _field_creates)
