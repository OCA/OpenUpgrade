from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, {"sale_order": [("effective_date", None)]})
