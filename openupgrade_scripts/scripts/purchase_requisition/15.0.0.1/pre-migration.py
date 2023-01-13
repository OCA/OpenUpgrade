from openupgradelib import openupgrade

_columns_copy = {
    "purchase_requisition": [
        ("description", None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _columns_copy)
