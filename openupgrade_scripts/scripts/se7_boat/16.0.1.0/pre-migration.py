from openupgradelib import openupgrade

_models_renames = [
    (
        "yacht.yacht",
        "boat.boat"
    )
]
_tables_renames = [
    (
        "yacht_yacht",
        "boat_boat"
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
