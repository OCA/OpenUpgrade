# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
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
