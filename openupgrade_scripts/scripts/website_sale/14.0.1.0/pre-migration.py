# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com/>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_model_renames = [
    ("product.style", "product.ribbon"),
]

_field_renames = [
    ("product.ribbon", "product_ribbon", "name", "html"),
]

_table_renames = [
    ("product_style", "product_ribbon"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
