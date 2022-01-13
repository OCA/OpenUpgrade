from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_hr_recruitment",
        [
            "hr_department_public",
            "hr_job_officer",
            "hr_job_portal",
            "hr_job_public",
        ],
        True,
    )
