from openupgradelib import openupgrade


def _remove_safety_xml_record(env):
    openupgrade.delete_records_safely_by_xml_id(
        env, ["purchase.mail_notification_confirm"]
    )


def _run_the_file_no_update_again(env):
    openupgrade.load_data(env.cr, "purchase", "16.0.1.2/noupdate_changes.xml")


@openupgrade.migrate()
def migrate(env, version):
    _remove_safety_xml_record(env)
    _run_the_file_no_update_again(env)
