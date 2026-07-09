# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def adjust_cron_interval(env):
    """
    If the sms cron has been left at default settings, use new default
    """
    cron = env.ref("sms.ir_cron_sms_scheduler_action")
    if cron and cron.interval_number == 1 and cron.interval_type == "hours":
        cron.interval_number = 24


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env,
        "sms",
        "19.0.3.0/noupdate_changes.xml",
        xml_transformation_filename="19.0.3.0/noupdate_changes-transformation.xml",
    )
    adjust_cron_interval(env)
