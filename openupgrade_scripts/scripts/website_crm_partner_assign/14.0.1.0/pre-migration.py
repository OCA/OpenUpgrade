from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [("crm.lead", "crm_lead", "date_assign", "date_partner_assign")],
    )

    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_crm_partner_assign",
        [
            "assigned_lead_portal_rule_1",
            "res_partner_grade_rule_portal_public",
        ],
        True,
    )
    # Remove SQL view crm_partner_report_assign not used anymore in Odoo v14.0
    openupgrade.logged_query(
        env.cr, "DROP VIEW IF EXISTS crm_partner_report_assign CASCADE"
    )
