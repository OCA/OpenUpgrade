# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

# pylint: disable=odoo-addons-relative-import
from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_renamed_xmlids = [
    ("l10n_fr.dom-tom", "base.dom-tom"),
    ("l10n_at.state_at_1", "base.state_at_1"),
    ("l10n_at.state_at_2", "base.state_at_2"),
    ("l10n_at.state_at_3", "base.state_at_3"),
    ("l10n_at.state_at_4", "base.state_at_4"),
    ("l10n_at.state_at_5", "base.state_at_5"),
    ("l10n_at.state_at_6", "base.state_at_6"),
    ("l10n_at.state_at_7", "base.state_at_7"),
    ("l10n_at.state_at_8", "base.state_at_8"),
    ("l10n_at.state_at_9", "base.state_at_9"),
    ("l10n_bd.state_bd_a", "base.state_bd_a"),
    ("l10n_bd.state_bd_b", "base.state_bd_b"),
    ("l10n_bd.state_bd_c", "base.state_bd_c"),
    ("l10n_bd.state_bd_d", "base.state_bd_d"),
    ("l10n_bd.state_bd_e", "base.state_bd_e"),
    ("l10n_bd.state_bd_f", "base.state_bd_f"),
    ("l10n_bd.state_bd_g", "base.state_bd_g"),
    ("l10n_bd.state_bd_h", "base.state_bd_h"),
    ("base.state_id_pp", "base.state_id_pe"),
    ("l10n_iq.state_iq_01", "base.state_iq_01"),
    ("l10n_iq.state_iq_01_ar", "base.state_iq_01_ar"),
    ("l10n_iq.state_iq_02", "base.state_iq_02"),
    ("l10n_iq.state_iq_02_ar", "base.state_iq_02_ar"),
    ("l10n_iq.state_iq_03", "base.state_iq_03"),
    ("l10n_iq.state_iq_03_ar", "base.state_iq_03_ar"),
    ("l10n_iq.state_iq_04", "base.state_iq_04"),
    ("l10n_iq.state_iq_04_ar", "base.state_iq_04_ar"),
    ("l10n_iq.state_iq_05", "base.state_iq_05"),
    ("l10n_iq.state_iq_05_ar", "base.state_iq_05_ar"),
    ("l10n_iq.state_iq_06", "base.state_iq_06"),
    ("l10n_iq.state_iq_06_ar", "base.state_iq_06_ar"),
    ("l10n_iq.state_iq_07", "base.state_iq_07"),
    ("l10n_iq.state_iq_07_ar", "base.state_iq_07_ar"),
    ("l10n_iq.state_iq_08", "base.state_iq_08"),
    ("l10n_iq.state_iq_08_ar", "base.state_iq_08_ar"),
    ("l10n_iq.state_iq_09", "base.state_iq_09"),
    ("l10n_iq.state_iq_09_ar", "base.state_iq_09_ar"),
    ("l10n_iq.state_iq_10", "base.state_iq_10"),
    ("l10n_iq.state_iq_10_ar", "base.state_iq_10_ar"),
    ("l10n_iq.state_iq_11", "base.state_iq_11"),
    ("l10n_iq.state_iq_11_ar", "base.state_iq_11_ar"),
    ("l10n_iq.state_iq_12", "base.state_iq_12"),
    ("l10n_iq.state_iq_12_ar", "base.state_iq_12_ar"),
    ("l10n_iq.state_iq_13", "base.state_iq_13"),
    ("l10n_iq.state_iq_13_ar", "base.state_iq_13_ar"),
    ("l10n_iq.state_iq_14", "base.state_iq_14"),
    ("l10n_iq.state_iq_14_ar", "base.state_iq_14_ar"),
    ("l10n_iq.state_iq_15", "base.state_iq_15"),
    ("l10n_iq.state_iq_15_ar", "base.state_iq_15_ar"),
    ("l10n_iq.state_iq_16", "base.state_iq_16"),
    ("l10n_iq.state_iq_16_ar", "base.state_iq_16_ar"),
    ("l10n_iq.state_iq_17", "base.state_iq_17"),
    ("l10n_iq.state_iq_17_ar", "base.state_iq_17_ar"),
    ("l10n_iq.state_iq_18", "base.state_iq_18"),
    ("l10n_iq.state_iq_18_ar", "base.state_iq_18_ar"),
    ("l10n_pk.state_pk_ajk", "base.state_pk_ajk"),
    ("l10n_pk.state_pk_ba", "base.state_pk_ba"),
    ("l10n_pk.state_pk_gb", "base.state_pk_gb"),
    ("l10n_pk.state_pk_is", "base.state_pk_is"),
    ("l10n_pk.state_pk_kp", "base.state_pk_kp"),
    ("l10n_pk.state_pk_pb", "base.state_pk_pb"),
    ("l10n_pk.state_pk_sd", "base.state_pk_sd"),
    ("l10n_pl.state_pl_ds", "base.state_pl_ds"),
    ("l10n_pl.state_pl_kp", "base.state_pl_kp"),
    ("l10n_pl.state_pl_lb", "base.state_pl_lb"),
    ("l10n_pl.state_pl_ld", "base.state_pl_ld"),
    ("l10n_pl.state_pl_ls", "base.state_pl_ls"),
    ("l10n_pl.state_pl_mp", "base.state_pl_mp"),
    ("l10n_pl.state_pl_mz", "base.state_pl_mz"),
    ("l10n_pl.state_pl_op", "base.state_pl_op"),
    ("l10n_pl.state_pl_pk", "base.state_pl_pk"),
    ("l10n_pl.state_pl_pl", "base.state_pl_pl"),
    ("l10n_pl.state_pl_pm", "base.state_pl_pm"),
    ("l10n_pl.state_pl_sk", "base.state_pl_sk"),
    ("l10n_pl.state_pl_sl", "base.state_pl_sl"),
    ("l10n_pl.state_pl_wm", "base.state_pl_wm"),
    ("l10n_pl.state_pl_wp", "base.state_pl_wp"),
    ("l10n_pl.state_pl_zp", "base.state_pl_zp"),
    ("l10n_tw.state_tw_chh", "base.state_tw_chh"),
    ("l10n_tw.state_tw_cic", "base.state_tw_cic"),
    ("l10n_tw.state_tw_cih", "base.state_tw_cih"),
    ("l10n_tw.state_tw_hch", "base.state_tw_hch"),
    ("l10n_tw.state_tw_hct", "base.state_tw_hct"),
    ("l10n_tw.state_tw_hlh", "base.state_tw_hlh"),
    ("l10n_tw.state_tw_ilh", "base.state_tw_ilh"),
    ("l10n_tw.state_tw_khc", "base.state_tw_khc"),
    ("l10n_tw.state_tw_klc", "base.state_tw_klc"),
    ("l10n_tw.state_tw_kmc", "base.state_tw_kmc"),
    ("l10n_tw.state_tw_lcc", "base.state_tw_lcc"),
    ("l10n_tw.state_tw_mlh", "base.state_tw_mlh"),
    ("l10n_tw.state_tw_ntc", "base.state_tw_ntc"),
    ("l10n_tw.state_tw_ntpc", "base.state_tw_ntpc"),
    ("l10n_tw.state_tw_phc", "base.state_tw_phc"),
    ("l10n_tw.state_tw_pth", "base.state_tw_pth"),
    ("l10n_tw.state_tw_tcc", "base.state_tw_tcc"),
    ("l10n_tw.state_tw_tnh", "base.state_tw_tnh"),
    ("l10n_tw.state_tw_tpc", "base.state_tw_tpc"),
    ("l10n_tw.state_tw_tth", "base.state_tw_tth"),
    ("l10n_tw.state_tw_tyc", "base.state_tw_tyc"),
    ("l10n_tw.state_tw_ylh", "base.state_tw_ylh"),
]

_merged_xmlids = [
    ("base.module_category_inventory", "base.module_category_supply_chain"),
    ("base.module_category_manufacturing", "base.module_category_supply_chain"),
]

_renamed_fields = [
    (
        "ir.actions.act_window",
        "ir_act_window",
        "groups_id",
        "group_ids",
    ),
    (
        "ir.actions.report",
        "ir_act_report_xml",
        "groups_id",
        "group_ids",
    ),
    (
        "ir.actions.server",
        "ir_act_report_xml",
        "groups_id",
        "group_ids",
    ),
    (
        "ir.ui.menu",
        "ir_ui_menu",
        "groups_id",
        "group_ids",
    ),
    (
        "ir.ui.view",
        "ir_ui_view",
        "groups_id",
        "group_ids",
    ),
    (
        "res.groups",
        "res_groups",
        "users",
        "user_ids",
    ),
    (
        "res.users",
        "res_users",
        "groups_id",
        "group_ids",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        f"""
        CREATE TABLE {
            openupgrade.get_legacy_name("ir_module_module")
        } AS (SELECT name, state FROM ir_module_module);
        """,
    )
    openupgrade.update_module_names(env.cr, renamed_modules.items())
    openupgrade.update_module_names(env.cr, merged_modules.items(), merge_modules=True)
    openupgrade.clean_transient_models(env.cr)
    openupgrade.rename_xmlids(env.cr, _renamed_xmlids)
    openupgrade.rename_xmlids(env.cr, _merged_xmlids, allow_merge=True)
    openupgrade.rename_fields(env, _renamed_fields)
