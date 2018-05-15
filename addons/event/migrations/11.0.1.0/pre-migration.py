# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def cleanup_translations(env):
    """
    Cleanup translations of adopted templates
    """
    updated_templates = (
        'event_reminder',
        'event_subscription',
    )
    openupgrade.delete_record_translations(env.cr, 'event', updated_templates)


@openupgrade.migrate()
def migrate(env, version):
    try:
        env.ref('event.report_event_registration_company_rule').unlink()
    except Exception:
        pass
    cleanup_translations(env)
