# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_lead_mobile(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE crm_lead
        SET phone = CONCAT(COALESCE(phone, ''), mobile)
        WHERE COALESCE(mobile, '') != ''
        """,
    )


def _load_data_pls_fields_param(env):
    # New PLS fields added in v19. Merge them into the existing value instead of
    # overwriting it, so a customized/removed `crm.pls_fields` param is preserved
    new_fields = {"state_id", "country_id", "source_id", "lang_id", "tag_ids"}
    param = env["ir.config_parameter"].sudo().get_param("crm.pls_fields")
    if param:
        current = set(param.split(","))
        merged = current | new_fields
        env["ir.config_parameter"].sudo().set_param(
            "crm.pls_fields", ",".join(sorted(merged))
        )


def _load_data_stage_colors(env):
    # Only color the default stages that still exist,
    # skip any the user deleted in v18.
    colors = {
        "stage_lead1": 11,
        "stage_lead2": 5,
        "stage_lead3": 8,
        "stage_lead4": 10,
    }
    for xml_id, color in colors.items():
        record = env.ref(f"crm.{xml_id}", raise_if_not_found=False)
        if record:
            record.color = color


@openupgrade.migrate()
def migrate(env, version):
    # Do not load noupdate_changes.xml: every entry is problematic (deleted stages,
    # customized pls param). the necessary changes are done manually in
    # the _load_data_* functions below

    openupgrade.m2o_to_x2m(env.cr, env["crm.stage"], "crm_stage", "team_ids", "team_id")
    _load_data_stage_colors(env)
    _load_data_pls_fields_param(env)
    _migrate_lead_mobile(env)
