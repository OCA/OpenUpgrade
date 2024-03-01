from openupgradelib import openupgrade

translations_to_delete = [
    "group_hr_recruitment_user",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "hr_recruitment", "16.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "hr_recruitment", translations_to_delete
    )
