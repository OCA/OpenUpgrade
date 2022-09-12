# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE crm_lead ADD recurring_revenue_monthly NUMERIC"
    )
    openupgrade.logged_query(
        env.cr, "ALTER TABLE crm_lead ADD recurring_revenue_monthly_prorated NUMERIC"
    )
    openupgrade.rename_fields(
        env,
        [
            ("crm.lead", "crm_lead", "expected_revenue", "prorated_revenue"),
            ("crm.lead", "crm_lead", "planned_revenue", "expected_revenue"),
        ],
    )
    openupgrade.rename_tables(env.cr, [("crm_lead_tag_rel", "crm_tag_rel")])
    openupgrade.remove_tables_fks(env.cr, ["crm_partner_binding"])
    # Disappeared constraint
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE crm_lead
           DROP CONSTRAINT IF EXISTS crm_lead_tag_name_uniq""",
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, ["crm.constraint_crm_lead_tag_name_uniq"]
    )
