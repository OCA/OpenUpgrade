# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fix_crm_reveal_rule_contact_filter_type(env):
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE crm_reveal_rule
        ADD COLUMN contact_filter_type varchar""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE crm_reveal_rule
        SET contact_filter_type = CASE
            WHEN seniority_id IS NOT NULL THEN 'seniority' ELSE 'role' END""")


@openupgrade.migrate()
def migrate(env, version):
    fix_crm_reveal_rule_contact_filter_type(env)
    openupgrade.load_data(env.cr, 'crm_iap_lead', 'migrations/13.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(env.cr, "crm_iap_lead", ["lead_generation_no_credits"])
