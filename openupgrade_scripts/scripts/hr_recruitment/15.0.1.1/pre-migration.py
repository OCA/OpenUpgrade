from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, "hr_recruitment", ["applicant_hired_template"], True
    )
    openupgrade.convert_field_to_html(
        env.cr, "hr_applicant", "description", "description"
    )
