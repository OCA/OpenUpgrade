# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_field_renames = [
    ("product.template", "product_template", "life_time", "expiration_time"),
    ("stock.production.lot", "stock_production_lot", "life_date", "expiration_date"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
