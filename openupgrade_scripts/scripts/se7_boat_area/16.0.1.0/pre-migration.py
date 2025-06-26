from openupgradelib import openupgrade

_models_renames = [
    (
        "yacht.area",
        "boat.area"
    )
]
_tables_renames = [
    (
        "yacht_area",
        "boat_area"
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
