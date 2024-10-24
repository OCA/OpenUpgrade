# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_models_renames = [
    ("restaurant.printer", "pos.printer"),
]

_tables_renames = [
    ("restaurant_printer", "pos_printer"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
