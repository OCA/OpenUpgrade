from openupgradelib import openupgrade

_models_renames = [
    ("account.invoice.tag", "account.move.tag"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _models_renames)
