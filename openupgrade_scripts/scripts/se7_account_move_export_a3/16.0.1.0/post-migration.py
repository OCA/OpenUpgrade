from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_names(
        env.cr,
        [("se7_pg_export_a3", "se7_account_move_export_a3")],
    )
