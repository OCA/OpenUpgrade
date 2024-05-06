from openupgradelib import openupgrade


def _merge_ir_


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "base", "17.0.1.3/noupdate_changes.xml")
