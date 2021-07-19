# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.table_exists(env.cr, "crm_lead_tag"):
        openupgrade.rename_models(
            env.cr,
            [
                ("crm.lead.tag", "crm.tag"),
            ],
        )
        openupgrade.rename_tables(
            env.cr,
            [
                ("crm_lead_tag", "crm_tag"),
            ],
        )
    openupgrade.set_xml_ids_noupdate_value(
        env, "sales_team", ["crm_rule_all_salesteam", "sale_team_comp_rule"], True
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            ("crm.crm_lead_tag_action", "sales_team.sales_team_crm_tag_action"),
            ("crm.crm_lead_tag_form", "sales_team.sales_team_crm_tag_view_form"),
            ("crm.crm_lead_tag_tree", "sales_team.sales_team_crm_tag_view_tree"),
            ("crm.access_crm_lead_tag", "sales_team.access_crm_tag"),
            ("crm.access_crm_lead_tag_manager", "sales_team.access_crm_tag_manager"),
            ("crm.access_crm_lead_tag_salesman", "sales_team.access_crm_tag_salesman"),
        ],
    )
