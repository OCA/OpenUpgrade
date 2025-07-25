from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "project", "18.0.1.3/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "project",
        ["mail_template_data_project_task", "rating_project_request_email_template"],
    )
