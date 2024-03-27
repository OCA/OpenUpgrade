from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "purchase_requisition", "14.0.0.1/noupdate_changes.xml"
    )
