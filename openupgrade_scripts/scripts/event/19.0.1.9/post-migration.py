# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def event_question(env):
    """
    Convert event_id, event_type_id to their many2many equivalents
    """
    openupgrade.m2o_to_x2m(
        env.cr, env["event.question"], "event_question", "event_ids", "event_id"
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env["event.question"],
        "event_question",
        "event_type_ids",
        "event_type_id",
    )


def adjust_cron_interval(env):
    """
    If the event mail cron has been left at default settings, use new default
    """
    cron = env.ref("event.event_mail_scheduler")
    if cron and cron.interval_number == 1 and cron.interval_type == "hours":
        cron.interval_number = 24


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env,
        "event",
        "19.0.1.9/noupdate_changes.xml",
        xml_transformation_filename="19.0.1.9/noupdate_changes-transformation.xml",
    )
    openupgrade.delete_record_translations(
        env.cr,
        "event",
        [
            "event_registration_mail_template_badge",
            "event_reminder",
            "event_subscription",
        ],
        ["body_html"],
    )
    event_question(env)
    adjust_cron_interval(env)
