from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "l10n_vn", "15.0.2.0.1/noupdate_changes.xml")
