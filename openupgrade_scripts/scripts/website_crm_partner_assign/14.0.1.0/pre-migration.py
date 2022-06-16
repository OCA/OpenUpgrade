# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ("crm.lead", "crm_lead", "date_assign", "date_partner_assign"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_crm_partner_assign",
        ["assigned_lead_portal_rule_1", "res_partner_grade_rule_portal_public"],
        True,
    )
