# Copyright 2019-2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'crm_reveal_role_crm_reveal_rule_rel': [
        ("crm_reveal_role_id", "crm_iap_lead_role_id"),
    ],
    'crm_reveal_industry_crm_reveal_rule_rel': [
        ("crm_reveal_industry_id", "crm_iap_lead_industry_id"),
    ],
}

_model_renames = [
    ("crm.reveal.industry", "crm.iap.lead.industry"),
    ("crm.reveal.role", "crm.iap.lead.role"),
    ("crm.reveal.seniority", "crm.iap.lead.seniority"),
]

_table_renames = [
    ("crm_reveal_industry", "crm_iap_lead_industry"),
    ("crm_reveal_role", "crm_iap_lead_role"),
    ("crm_reveal_seniority", "crm_iap_lead_seniority"),
    ("crm_reveal_role_crm_reveal_rule_rel", "crm_iap_lead_role_crm_reveal_rule_rel"),
    ("crm_reveal_industry_crm_reveal_rule_rel", "crm_iap_lead_industry_crm_reveal_rule_rel"),
]

_xmlid_renames = [
    ("crm_iap_lead.crm_reveal_rule_action", "crm_iap_lead_website.crm_reveal_rule_action"),
    ("crm_iap_lead.crm_reveal_view_action", "crm_iap_lead_website.crm_reveal_view_action"),
    ("crm_iap_lead.ir_cron_crm_reveal_lead", "crm_iap_lead_website.ir_cron_crm_reveal_lead"),
    ("crm_iap_lead.access_crm_reveal_rule", "crm_iap_lead_website.access_crm_reveal_rule"),
    ("crm_iap_lead.access_crm_reveal_view", "crm_iap_lead_website.access_crm_reveal_view"),
    ("crm_iap_lead.crm_reveal_rule_menu_action", "crm_iap_lead_website.crm_reveal_rule_menu_action"),
    ("crm_iap_lead.crm_reveal_view_menu_action", "crm_iap_lead_website.crm_reveal_view_menu_action"),
    ("crm_iap_lead.reveal_no_credits", "crm_iap_lead.lead_generation_no_credits"),
    ("crm_iap_lead.access_crm_reveal_industry", "crm_iap_lead.access_crm_iap_lead_industry"),
    ("crm_iap_lead.access_crm_reveal_role", "crm_iap_lead.access_crm_iap_lead_role"),
    ("crm_iap_lead.access_crm_reveal_seniority", "crm_iap_lead.access_crm_iap_lead_seniority"),
]


def model_xmlid_renames(env):
    xmlid = "crm_iap_lead.{table}_{number}"
    openupgrade.rename_xmlids(env.cr, [
        (xmlid.format(table="crm_reveal_seniority", number=number),
         xmlid.format(table="crm_iap_lead_seniority", number=number))
        for number in list(range(1, 4, 1))])
    openupgrade.rename_xmlids(env.cr, [
        (xmlid.format(table="crm_reveal_role", number=number),
         xmlid.format(table="crm_iap_lead_role", number=number))
        for number in list(range(1, 23, 1))])
    numbers = [30, 33, 69, 86, 114, 136, 138, 146, 148, 149, 150, 151, 152, 153, 154,
               155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168]
    openupgrade.rename_xmlids(env.cr, [
        (xmlid.format(table="crm_reveal_industry", number=number),
         xmlid.format(table="crm_iap_lead_industry", number=number))
        for number in numbers])


def install_new_modules(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_module_module
        SET state='to install'
        WHERE name = 'crm_iap_lead_website' AND state='uninstalled'""")


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    model_xmlid_renames(env)
    install_new_modules(env)
