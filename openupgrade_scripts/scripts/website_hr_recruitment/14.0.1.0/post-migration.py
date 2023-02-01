from openupgradelib import openupgrade, openupgrade_140


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["website_hr_recruitment.menu_jobs"],
    )
    openupgrade_140.convert_field_html_string_13to14(
        env,
        "hr.job",
        "website_description",
    )
