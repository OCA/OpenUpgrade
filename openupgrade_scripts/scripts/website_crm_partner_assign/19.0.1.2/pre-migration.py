# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

xmlid_renames = [
    (
        "website_crm_partner_assign.res_partner_grade_action",
        "partnership.res_partner_grade_action",
    ),
    (
        "website_crm_partner_assign.access_res_partner_grade",
        "partnership.access_res_partner_grade",
    ),
    (
        "website_crm_partner_assign.access_res_partner_grade_manager",
        "partnership.access_res_partner_grade_manager",
    ),
    (
        "website_crm_partner_assign.menu_res_partner_grade_action",
        "partnership.menu_res_partner_grade_action",
    ),
    (
        "website_crm_partner_assign.res_partner_grade_data_bronze",
        "partnership.res_partner_grade_data_bronze",
    ),
    (
        "website_crm_partner_assign.res_partner_grade_data_gold",
        "partnership.res_partner_grade_data_gold",
    ),
    (
        "website_crm_partner_assign.res_partner_grade_data_silver",
        "partnership.res_partner_grade_data_silver",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    for old_xmlid, new_xmlid in xmlid_renames:
        old_mod, old_name = old_xmlid.split(".", 1)
        new_mod, new_name = new_xmlid.split(".", 1)
        cr.execute(
            "SELECT 1 FROM ir_model_data WHERE module = %s AND name = %s",
            (new_mod, new_name),
        )
        if cr.fetchone():
            openupgrade.logged_query(
                cr,
                "DELETE FROM ir_model_data WHERE module = %s AND name = %s",
                (old_mod, old_name),
            )
        else:
            openupgrade.rename_xmlids(cr, [(old_xmlid, new_xmlid)])
