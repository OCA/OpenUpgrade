from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_holidays", "18.0.1.6/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "hr_holidays", ["mt_leave_allocation"], ["name"]
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, ["hr_holidays.mt_leave_home_working"]
    )
