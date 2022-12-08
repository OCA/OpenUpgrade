from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "mass_mailing", "15.0.2.5/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "mass_mailing",
        ["ir_cron_mass_mailing_queue"],
    )
