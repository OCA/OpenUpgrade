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
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
