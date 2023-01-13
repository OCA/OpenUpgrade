from openupgradelib import openupgrade

_columns_copy = {
    "sale_order_template": [
        ("note", None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _columns_copy)
