from openupgradelib import openupgrade

_columns_copy = {
    "hr_contract": [
        ("notes", None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _columns_copy)
