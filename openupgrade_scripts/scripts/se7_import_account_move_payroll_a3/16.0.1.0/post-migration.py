from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_names(
        env.cr,
        [("se7_import_nominas_a3", "se7_import_account_move_payroll_a3")],
    )
