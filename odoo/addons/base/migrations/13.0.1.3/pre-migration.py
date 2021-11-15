# Copyright 2020 Andrii Skrypka
# Copyright 2020 Opener B.V. (stefan@opener.amsterdam)
# Copyright 2019-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import csv
from openupgradelib import openupgrade
from openupgradelib import openupgrade_merge_records
from odoo.addons.openupgrade_records.lib import apriori
from odoo.modules.module import get_module_resource


xmlid_renames_res_country_state = [
    ('base.state_mx_q roo', 'base.state_mx_q_roo'),
    ('l10n_ro.RO_AB', 'base.RO_AB'),
    ('l10n_ro.RO_AG', 'base.RO_AG'),
    ('l10n_ro.RO_AR', 'base.RO_AR'),
    ('l10n_ro.RO_B', 'base.RO_B'),
    ('l10n_ro.RO_BC', 'base.RO_BC'),
    ('l10n_ro.RO_BH', 'base.RO_BH'),
    ('l10n_ro.RO_BN', 'base.RO_BN'),
    ('l10n_ro.RO_BR', 'base.RO_BR'),
    ('l10n_ro.RO_BT', 'base.RO_BT'),
    ('l10n_ro.RO_BV', 'base.RO_BV'),
    ('l10n_ro.RO_BZ', 'base.RO_BZ'),
    ('l10n_ro.RO_CJ', 'base.RO_CJ'),
    ('l10n_ro.RO_CL', 'base.RO_CL'),
    ('l10n_ro.RO_CS', 'base.RO_CS'),
    ('l10n_ro.RO_CT', 'base.RO_CT'),
    ('l10n_ro.RO_CV', 'base.RO_CV'),
    ('l10n_ro.RO_DB', 'base.RO_DB'),
    ('l10n_ro.RO_DJ', 'base.RO_DJ'),
    ('l10n_ro.RO_GJ', 'base.RO_GJ'),
    ('l10n_ro.RO_GL', 'base.RO_GL'),
    ('l10n_ro.RO_GR', 'base.RO_GR'),
    ('l10n_ro.RO_HD', 'base.RO_HD'),
    ('l10n_ro.RO_HR', 'base.RO_HR'),
    ('l10n_ro.RO_IF', 'base.RO_IF'),
    ('l10n_ro.RO_IL', 'base.RO_IL'),
    ('l10n_ro.RO_IS', 'base.RO_IS'),
    ('l10n_ro.RO_MH', 'base.RO_MH'),
    ('l10n_ro.RO_MM', 'base.RO_MM'),
    ('l10n_ro.RO_MS', 'base.RO_MS'),
    ('l10n_ro.RO_NT', 'base.RO_NT'),
    ('l10n_ro.RO_OT', 'base.RO_OT'),
    ('l10n_ro.RO_PH', 'base.RO_PH'),
    ('l10n_ro.RO_SB', 'base.RO_SB'),
    ('l10n_ro.RO_SJ', 'base.RO_SJ'),
    ('l10n_ro.RO_SM', 'base.RO_SM'),
    ('l10n_ro.RO_SV', 'base.RO_SV'),
    ('l10n_ro.RO_TL', 'base.RO_TL'),
    ('l10n_ro.RO_TM', 'base.RO_TM'),
    ('l10n_ro.RO_TR', 'base.RO_TR'),
    ('l10n_ro.RO_VL', 'base.RO_VL'),
    ('l10n_ro.RO_VN', 'base.RO_VN'),
    ('l10n_ro.RO_VS', 'base.RO_VS'),
    ('l10n_cr.state_A', 'base.state_A'),
    ('l10n_cr.state_C', 'base.state_C'),
    ('l10n_cr.state_G', 'base.state_G'),
    ('l10n_cr.state_H', 'base.state_H'),
    ('l10n_cr.state_L', 'base.state_L'),
    ('l10n_cr.state_P', 'base.state_P'),
    ('l10n_cr.state_SJ', 'base.state_SJ'),
    ('l10n_do.state_DO_01', 'base.state_DO_01'),
    ('l10n_do.state_DO_02', 'base.state_DO_02'),
    ('l10n_do.state_DO_03', 'base.state_DO_03'),
    ('l10n_do.state_DO_4', 'base.state_DO_04'),
    ('l10n_do.state_DO_05', 'base.state_DO_05'),
    ('l10n_do.state_DO_06', 'base.state_DO_06'),
    ('l10n_do.state_DO_07', 'base.state_DO_07'),
    ('l10n_do.state_DO_08', 'base.state_DO_08'),
    ('l10n_do.state_DO_09', 'base.state_DO_09'),
    ('l10n_do.state_DO_10', 'base.state_DO_10'),
    ('l10n_do.state_DO_11', 'base.state_DO_11'),
    ('l10n_do.state_DO_12', 'base.state_DO_12'),
    ('l10n_do.state_DO_13', 'base.state_DO_13'),
    ('l10n_do.state_DO_14', 'base.state_DO_14'),
    ('l10n_do.state_DO_15', 'base.state_DO_15'),
    ('l10n_do.state_DO_16', 'base.state_DO_16'),
    ('l10n_do.state_DO_17', 'base.state_DO_17'),
    ('l10n_do.state_DO_18', 'base.state_DO_18'),
    ('l10n_do.state_DO_19', 'base.state_DO_19'),
    ('l10n_do.state_DO_20', 'base.state_DO_20'),
    ('l10n_do.state_DO_21', 'base.state_DO_21'),
    ('l10n_do.state_DO_22', 'base.state_DO_22'),
    ('l10n_do.state_DO_23', 'base.state_DO_23'),
    ('l10n_do.state_DO_24', 'base.state_DO_24'),
    ('l10n_do.state_DO_25', 'base.state_DO_25'),
    ('l10n_do.state_DO_26', 'base.state_DO_26'),
    ('l10n_do.state_DO_27', 'base.state_DO_27'),
    ('l10n_do.state_DO_28', 'base.state_DO_28'),
    ('l10n_do.state_DO_29', 'base.state_DO_29'),
    ('l10n_do.state_DO_30', 'base.state_DO_30'),
    ('l10n_do.state_DO_31', 'base.state_DO_31'),
    ('l10n_do.state_DO_32', 'base.state_DO_32'),
    ('l10n_cn.state_AH', 'base.state_cn_AH'),
    ('l10n_cn.state_BJ', 'base.state_cn_BJ'),
    ('l10n_cn.state_CQ', 'base.state_cn_CQ'),
    ('l10n_cn.state_FJ', 'base.state_cn_FJ'),
    ('l10n_cn.state_GD', 'base.state_cn_GD'),
    ('l10n_cn.state_GS', 'base.state_cn_GS'),
    ('l10n_cn.state_GX', 'base.state_cn_GX'),
    ('l10n_cn.state_GZ', 'base.state_cn_GZ'),
    ('l10n_cn.state_HA', 'base.state_cn_HA'),
    ('l10n_cn.state_HB', 'base.state_cn_HB'),
    ('l10n_cn.state_HE', 'base.state_cn_HE'),
    ('l10n_cn.state_HI', 'base.state_cn_HI'),
    ('l10n_cn.state_HK', 'base.state_cn_HK'),
    ('l10n_cn.state_HL', 'base.state_cn_HL'),
    ('l10n_cn.state_HN', 'base.state_cn_HN'),
    ('l10n_cn.state_JL', 'base.state_cn_JL'),
    ('l10n_cn.state_JS', 'base.state_cn_JS'),
    ('l10n_cn.state_JX', 'base.state_cn_JX'),
    ('l10n_cn.state_LN', 'base.state_cn_LN'),
    ('l10n_cn.state_MO', 'base.state_cn_MO'),
    ('l10n_cn.state_NM', 'base.state_cn_NM'),
    ('l10n_cn.state_NX', 'base.state_cn_NX'),
    ('l10n_cn.state_QH', 'base.state_cn_QH'),
    ('l10n_cn.state_SC', 'base.state_cn_SC'),
    ('l10n_cn.state_SD', 'base.state_cn_SD'),
    ('l10n_cn.state_SH', 'base.state_cn_SH'),
    ('l10n_cn.state_SN', 'base.state_cn_SN'),
    ('l10n_cn.state_SX', 'base.state_cn_SX'),
    ('l10n_cn.state_TJ', 'base.state_cn_TJ'),
    ('l10n_cn.state_TW', 'base.state_cn_TW'),
    ('l10n_cn.state_XJ', 'base.state_cn_XJ'),
    ('l10n_cn.state_XZ', 'base.state_cn_XZ'),
    ('l10n_cn.state_YN', 'base.state_cn_YN'),
    ('l10n_cn.state_ZJ', 'base.state_cn_ZJ'),
    ('l10n_et.state_et_1', 'base.state_et_1'),
    ('l10n_et.state_et_10', 'base.state_et_10'),
    ('l10n_et.state_et_11', 'base.state_et_11'),
    ('l10n_et.state_et_2', 'base.state_et_2'),
    ('l10n_et.state_et_3', 'base.state_et_3'),
    ('l10n_et.state_et_4', 'base.state_et_4'),
    ('l10n_et.state_et_5', 'base.state_et_5'),
    ('l10n_et.state_et_6', 'base.state_et_6'),
    ('l10n_et.state_et_7', 'base.state_et_7'),
    ('l10n_et.state_et_8', 'base.state_et_8'),
    ('l10n_et.state_et_9', 'base.state_et_9'),
    ('l10n_ie.state_ie_1', 'base.state_ie_1'),
    ('l10n_ie.state_ie_10', 'base.state_ie_10'),
    ('l10n_ie.state_ie_11', 'base.state_ie_11'),
    ('l10n_ie.state_ie_12', 'base.state_ie_12'),
    ('l10n_ie.state_ie_13', 'base.state_ie_13'),
    ('l10n_ie.state_ie_14', 'base.state_ie_14'),
    ('l10n_ie.state_ie_15', 'base.state_ie_15'),
    ('l10n_ie.state_ie_16', 'base.state_ie_16'),
    ('l10n_ie.state_ie_17', 'base.state_ie_17'),
    ('l10n_ie.state_ie_18', 'base.state_ie_18'),
    ('l10n_ie.state_ie_19', 'base.state_ie_19'),
    ('l10n_ie.state_ie_2', 'base.state_ie_2'),
    ('l10n_ie.state_ie_20', 'base.state_ie_20'),
    ('l10n_ie.state_ie_21', 'base.state_ie_21'),
    ('l10n_ie.state_ie_22', 'base.state_ie_22'),
    ('l10n_ie.state_ie_23', 'base.state_ie_23'),
    ('l10n_ie.state_ie_24', 'base.state_ie_24'),
    ('l10n_ie.state_ie_25', 'base.state_ie_25'),
    ('l10n_ie.state_ie_26', 'base.state_ie_26'),
    ('l10n_ie.state_ie_27', 'base.state_ie_27'),
    ('l10n_ie.state_ie_28', 'base.state_ie_28'),
    ('l10n_ie.state_ie_29', 'base.state_ie_29'),
    ('l10n_ie.state_ie_3', 'base.state_ie_3'),
    ('l10n_ie.state_ie_30', 'base.state_ie_30'),
    ('l10n_ie.state_ie_31', 'base.state_ie_31'),
    ('l10n_ie.state_ie_32', 'base.state_ie_32'),
    ('l10n_ie.state_ie_4', 'base.state_ie_4'),
    ('l10n_ie.state_ie_5', 'base.state_ie_5'),
    ('l10n_ie.state_ie_6', 'base.state_ie_6'),
    ('l10n_ie.state_ie_7', 'base.state_ie_7'),
    ('l10n_ie.state_ie_8', 'base.state_ie_8'),
    ('l10n_ie.state_ie_9', 'base.state_ie_9'),
    ('l10n_nl.state_nl_bq1', 'base.state_nl_bq1'),
    ('l10n_nl.state_nl_bq2', 'base.state_nl_bq2'),
    ('l10n_nl.state_nl_bq3', 'base.state_nl_bq3'),
    ('l10n_nl.state_nl_dr', 'base.state_nl_dr'),
    ('l10n_nl.state_nl_fl', 'base.state_nl_fl'),
    ('l10n_nl.state_nl_fr', 'base.state_nl_fr'),
    ('l10n_nl.state_nl_ge', 'base.state_nl_ge'),
    ('l10n_nl.state_nl_gr', 'base.state_nl_gr'),
    ('l10n_nl.state_nl_li', 'base.state_nl_li'),
    ('l10n_nl.state_nl_nb', 'base.state_nl_nb'),
    ('l10n_nl.state_nl_nh', 'base.state_nl_nh'),
    ('l10n_nl.state_nl_ov', 'base.state_nl_ov'),
    ('l10n_nl.state_nl_ut', 'base.state_nl_ut'),
    ('l10n_nl.state_nl_ze', 'base.state_nl_ze'),
    ('l10n_nl.state_nl_zh', 'base.state_nl_zh'),
    ('l10n_tr.state_tr_01', 'base.state_tr_01'),
    ('l10n_tr.state_tr_02', 'base.state_tr_02'),
    ('l10n_tr.state_tr_03', 'base.state_tr_03'),
    ('l10n_tr.state_tr_04', 'base.state_tr_04'),
    ('l10n_tr.state_tr_05', 'base.state_tr_05'),
    ('l10n_tr.state_tr_06', 'base.state_tr_06'),
    ('l10n_tr.state_tr_07', 'base.state_tr_07'),
    ('l10n_tr.state_tr_08', 'base.state_tr_08'),
    ('l10n_tr.state_tr_09', 'base.state_tr_09'),
    ('l10n_tr.state_tr_10', 'base.state_tr_10'),
    ('l10n_tr.state_tr_11', 'base.state_tr_11'),
    ('l10n_tr.state_tr_12', 'base.state_tr_12'),
    ('l10n_tr.state_tr_13', 'base.state_tr_13'),
    ('l10n_tr.state_tr_14', 'base.state_tr_14'),
    ('l10n_tr.state_tr_15', 'base.state_tr_15'),
    ('l10n_tr.state_tr_16', 'base.state_tr_16'),
    ('l10n_tr.state_tr_17', 'base.state_tr_17'),
    ('l10n_tr.state_tr_18', 'base.state_tr_18'),
    ('l10n_tr.state_tr_19', 'base.state_tr_19'),
    ('l10n_tr.state_tr_20', 'base.state_tr_20'),
    ('l10n_tr.state_tr_21', 'base.state_tr_21'),
    ('l10n_tr.state_tr_22', 'base.state_tr_22'),
    ('l10n_tr.state_tr_23', 'base.state_tr_23'),
    ('l10n_tr.state_tr_24', 'base.state_tr_24'),
    ('l10n_tr.state_tr_25', 'base.state_tr_25'),
    ('l10n_tr.state_tr_26', 'base.state_tr_26'),
    ('l10n_tr.state_tr_27', 'base.state_tr_27'),
    ('l10n_tr.state_tr_28', 'base.state_tr_28'),
    ('l10n_tr.state_tr_29', 'base.state_tr_29'),
    ('l10n_tr.state_tr_30', 'base.state_tr_30'),
    ('l10n_tr.state_tr_31', 'base.state_tr_31'),
    ('l10n_tr.state_tr_32', 'base.state_tr_32'),
    ('l10n_tr.state_tr_33', 'base.state_tr_33'),
    ('l10n_tr.state_tr_34', 'base.state_tr_34'),
    ('l10n_tr.state_tr_35', 'base.state_tr_35'),
    ('l10n_tr.state_tr_36', 'base.state_tr_36'),
    ('l10n_tr.state_tr_37', 'base.state_tr_37'),
    ('l10n_tr.state_tr_38', 'base.state_tr_38'),
    ('l10n_tr.state_tr_39', 'base.state_tr_39'),
    ('l10n_tr.state_tr_40', 'base.state_tr_40'),
    ('l10n_tr.state_tr_41', 'base.state_tr_41'),
    ('l10n_tr.state_tr_42', 'base.state_tr_42'),
    ('l10n_tr.state_tr_43', 'base.state_tr_43'),
    ('l10n_tr.state_tr_44', 'base.state_tr_44'),
    ('l10n_tr.state_tr_45', 'base.state_tr_45'),
    ('l10n_tr.state_tr_46', 'base.state_tr_46'),
    ('l10n_tr.state_tr_47', 'base.state_tr_47'),
    ('l10n_tr.state_tr_48', 'base.state_tr_48'),
    ('l10n_tr.state_tr_49', 'base.state_tr_49'),
    ('l10n_tr.state_tr_50', 'base.state_tr_50'),
    ('l10n_tr.state_tr_51', 'base.state_tr_51'),
    ('l10n_tr.state_tr_52', 'base.state_tr_52'),
    ('l10n_tr.state_tr_53', 'base.state_tr_53'),
    ('l10n_tr.state_tr_54', 'base.state_tr_54'),
    ('l10n_tr.state_tr_55', 'base.state_tr_55'),
    ('l10n_tr.state_tr_56', 'base.state_tr_56'),
    ('l10n_tr.state_tr_57', 'base.state_tr_57'),
    ('l10n_tr.state_tr_58', 'base.state_tr_58'),
    ('l10n_tr.state_tr_59', 'base.state_tr_59'),
    ('l10n_tr.state_tr_60', 'base.state_tr_60'),
    ('l10n_tr.state_tr_61', 'base.state_tr_61'),
    ('l10n_tr.state_tr_62', 'base.state_tr_62'),
    ('l10n_tr.state_tr_63', 'base.state_tr_63'),
    ('l10n_tr.state_tr_64', 'base.state_tr_64'),
    ('l10n_tr.state_tr_65', 'base.state_tr_65'),
    ('l10n_tr.state_tr_66', 'base.state_tr_66'),
    ('l10n_tr.state_tr_67', 'base.state_tr_67'),
    ('l10n_tr.state_tr_68', 'base.state_tr_68'),
    ('l10n_tr.state_tr_69', 'base.state_tr_69'),
    ('l10n_tr.state_tr_70', 'base.state_tr_70'),
    ('l10n_tr.state_tr_71', 'base.state_tr_71'),
    ('l10n_tr.state_tr_72', 'base.state_tr_72'),
    ('l10n_tr.state_tr_73', 'base.state_tr_73'),
    ('l10n_tr.state_tr_74', 'base.state_tr_74'),
    ('l10n_tr.state_tr_75', 'base.state_tr_75'),
    ('l10n_tr.state_tr_76', 'base.state_tr_76'),
    ('l10n_tr.state_tr_77', 'base.state_tr_77'),
    ('l10n_tr.state_tr_78', 'base.state_tr_78'),
    ('l10n_tr.state_tr_79', 'base.state_tr_79'),
    ('l10n_tr.state_tr_80', 'base.state_tr_80'),
    ('l10n_tr.state_tr_81', 'base.state_tr_81'),
    ('l10n_uk.state_uk_1', 'base.state_uk1'),
    ('l10n_uk.state_uk_10', 'base.state_uk10'),
    ('l10n_uk.state_uk_100', 'base.state_uk100'),
    ('l10n_uk.state_uk_101', 'base.state_uk101'),
    ('l10n_uk.state_uk_102', 'base.state_uk102'),
    ('l10n_uk.state_uk_103', 'base.state_uk103'),
    ('l10n_uk.state_uk_104', 'base.state_uk104'),
    ('l10n_uk.state_uk_105', 'base.state_uk105'),
    ('l10n_uk.state_uk_106', 'base.state_uk106'),
    ('l10n_uk.state_uk_107', 'base.state_uk107'),
    ('l10n_uk.state_uk_108', 'base.state_uk108'),
    ('l10n_uk.state_uk_109', 'base.state_uk109'),
    ('l10n_uk.state_uk_11', 'base.state_uk11'),
    ('l10n_uk.state_uk_110', 'base.state_uk110'),
    ('l10n_uk.state_uk_111', 'base.state_uk111'),
    ('l10n_uk.state_uk_112', 'base.state_uk112'),
    ('l10n_uk.state_uk_113', 'base.state_uk113'),
    ('l10n_uk.state_uk_114', 'base.state_uk114'),
    ('l10n_uk.state_uk_115', 'base.state_uk115'),
    ('l10n_uk.state_uk_116', 'base.state_uk116'),
    ('l10n_uk.state_uk_117', 'base.state_uk117'),
    ('l10n_uk.state_uk_118', 'base.state_uk118'),
    ('l10n_uk.state_uk_119', 'base.state_uk119'),
    ('l10n_uk.state_uk_12', 'base.state_uk12'),
    ('l10n_uk.state_uk_13', 'base.state_uk13'),
    ('l10n_uk.state_uk_14', 'base.state_uk14'),
    ('l10n_uk.state_uk_15', 'base.state_uk15'),
    ('l10n_uk.state_uk_16', 'base.state_uk16'),
    ('l10n_uk.state_uk_17', 'base.state_uk17'),
    ('l10n_uk.state_uk_18', 'base.state_uk18'),
    ('l10n_uk.state_uk_19', 'base.state_uk19'),
    ('l10n_uk.state_uk_2', 'base.state_uk2'),
    ('l10n_uk.state_uk_20', 'base.state_uk20'),
    ('l10n_uk.state_uk_21', 'base.state_uk21'),
    ('l10n_uk.state_uk_22', 'base.state_uk22'),
    ('l10n_uk.state_uk_23', 'base.state_uk23'),
    ('l10n_uk.state_uk_24', 'base.state_uk24'),
    ('l10n_uk.state_uk_25', 'base.state_uk25'),
    ('l10n_uk.state_uk_26', 'base.state_uk26'),
    ('l10n_uk.state_uk_27', 'base.state_uk27'),
    ('l10n_uk.state_uk_28', 'base.state_uk28'),
    ('l10n_uk.state_uk_29', 'base.state_uk29'),
    ('l10n_uk.state_uk_3', 'base.state_uk3'),
    ('l10n_uk.state_uk_30', 'base.state_uk30'),
    ('l10n_uk.state_uk_31', 'base.state_uk31'),
    ('l10n_uk.state_uk_32', 'base.state_uk32'),
    ('l10n_uk.state_uk_33', 'base.state_uk33'),
    ('l10n_uk.state_uk_34', 'base.state_uk34'),
    ('l10n_uk.state_uk_35', 'base.state_uk35'),
    ('l10n_uk.state_uk_36', 'base.state_uk36'),
    ('l10n_uk.state_uk_37', 'base.state_uk37'),
    ('l10n_uk.state_uk_38', 'base.state_uk38'),
    ('l10n_uk.state_uk_39', 'base.state_uk39'),
    ('l10n_uk.state_uk_4', 'base.state_uk4'),
    ('l10n_uk.state_uk_40', 'base.state_uk40'),
    ('l10n_uk.state_uk_41', 'base.state_uk41'),
    ('l10n_uk.state_uk_42', 'base.state_uk42'),
    ('l10n_uk.state_uk_43', 'base.state_uk43'),
    ('l10n_uk.state_uk_44', 'base.state_uk44'),
    ('l10n_uk.state_uk_45', 'base.state_uk45'),
    ('l10n_uk.state_uk_46', 'base.state_uk46'),
    ('l10n_uk.state_uk_47', 'base.state_uk47'),
    ('l10n_uk.state_uk_48', 'base.state_uk48'),
    ('l10n_uk.state_uk_49', 'base.state_uk49'),
    ('l10n_uk.state_uk_5', 'base.state_uk5'),
    ('l10n_uk.state_uk_50', 'base.state_uk50'),
    ('l10n_uk.state_uk_51', 'base.state_uk51'),
    ('l10n_uk.state_uk_52', 'base.state_uk52'),
    ('l10n_uk.state_uk_53', 'base.state_uk53'),
    ('l10n_uk.state_uk_54', 'base.state_uk54'),
    ('l10n_uk.state_uk_55', 'base.state_uk55'),
    ('l10n_uk.state_uk_56', 'base.state_uk56'),
    ('l10n_uk.state_uk_57', 'base.state_uk57'),
    ('l10n_uk.state_uk_58', 'base.state_uk58'),
    ('l10n_uk.state_uk_59', 'base.state_uk59'),
    ('l10n_uk.state_uk_6', 'base.state_uk6'),
    ('l10n_uk.state_uk_60', 'base.state_uk60'),
    ('l10n_uk.state_uk_61', 'base.state_uk61'),
    ('l10n_uk.state_uk_62', 'base.state_uk62'),
    ('l10n_uk.state_uk_63', 'base.state_uk63'),
    ('l10n_uk.state_uk_64', 'base.state_uk64'),
    ('l10n_uk.state_uk_65', 'base.state_uk65'),
    ('l10n_uk.state_uk_66', 'base.state_uk66'),
    ('l10n_uk.state_uk_67', 'base.state_uk67'),
    ('l10n_uk.state_uk_68', 'base.state_uk68'),
    ('l10n_uk.state_uk_69', 'base.state_uk69'),
    ('l10n_uk.state_uk_7', 'base.state_uk7'),
    ('l10n_uk.state_uk_70', 'base.state_uk70'),
    ('l10n_uk.state_uk_71', 'base.state_uk71'),
    ('l10n_uk.state_uk_72', 'base.state_uk72'),
    ('l10n_uk.state_uk_73', 'base.state_uk73'),
    ('l10n_uk.state_uk_74', 'base.state_uk74'),
    ('l10n_uk.state_uk_75', 'base.state_uk75'),
    ('l10n_uk.state_uk_76', 'base.state_uk76'),
    ('l10n_uk.state_uk_77', 'base.state_uk77'),
    ('l10n_uk.state_uk_78', 'base.state_uk78'),
    ('l10n_uk.state_uk_79', 'base.state_uk79'),
    ('l10n_uk.state_uk_8', 'base.state_uk8'),
    ('l10n_uk.state_uk_80', 'base.state_uk80'),
    ('l10n_uk.state_uk_81', 'base.state_uk81'),
    ('l10n_uk.state_uk_82', 'base.state_uk82'),
    ('l10n_uk.state_uk_83', 'base.state_uk83'),
    ('l10n_uk.state_uk_84', 'base.state_uk84'),
    ('l10n_uk.state_uk_85', 'base.state_uk85'),
    ('l10n_uk.state_uk_86', 'base.state_uk86'),
    ('l10n_uk.state_uk_87', 'base.state_uk87'),
    ('l10n_uk.state_uk_88', 'base.state_uk88'),
    ('l10n_uk.state_uk_89', 'base.state_uk89'),
    ('l10n_uk.state_uk_9', 'base.state_uk9'),
    ('l10n_uk.state_uk_90', 'base.state_uk90'),
    ('l10n_uk.state_uk_91', 'base.state_uk91'),
    ('l10n_uk.state_uk_92', 'base.state_uk92'),
    ('l10n_uk.state_uk_93', 'base.state_uk93'),
    ('l10n_uk.state_uk_94', 'base.state_uk94'),
    ('l10n_uk.state_uk_95', 'base.state_uk95'),
    ('l10n_uk.state_uk_96', 'base.state_uk96'),
    ('l10n_uk.state_uk_97', 'base.state_uk97'),
    ('l10n_uk.state_uk_98', 'base.state_uk98'),
    ('l10n_uk.state_uk_99', 'base.state_uk99'),
    ('l10n_vn.state_vn_VN-01', 'base.state_vn_VN-01'),
    ('l10n_vn.state_vn_VN-02', 'base.state_vn_VN-02'),
    ('l10n_vn.state_vn_VN-03', 'base.state_vn_VN-03'),
    ('l10n_vn.state_vn_VN-04', 'base.state_vn_VN-04'),
    ('l10n_vn.state_vn_VN-05', 'base.state_vn_VN-05'),
    ('l10n_vn.state_vn_VN-06', 'base.state_vn_VN-06'),
    ('l10n_vn.state_vn_VN-07', 'base.state_vn_VN-07'),
    ('l10n_vn.state_vn_VN-09', 'base.state_vn_VN-09'),
    ('l10n_vn.state_vn_VN-13', 'base.state_vn_VN-13'),
    ('l10n_vn.state_vn_VN-14', 'base.state_vn_VN-14'),
    ('l10n_vn.state_vn_VN-18', 'base.state_vn_VN-18'),
    ('l10n_vn.state_vn_VN-20', 'base.state_vn_VN-20'),
    ('l10n_vn.state_vn_VN-21', 'base.state_vn_VN-21'),
    ('l10n_vn.state_vn_VN-22', 'base.state_vn_VN-22'),
    ('l10n_vn.state_vn_VN-23', 'base.state_vn_VN-23'),
    ('l10n_vn.state_vn_VN-24', 'base.state_vn_VN-24'),
    ('l10n_vn.state_vn_VN-25', 'base.state_vn_VN-25'),
    ('l10n_vn.state_vn_VN-26', 'base.state_vn_VN-26'),
    ('l10n_vn.state_vn_VN-27', 'base.state_vn_VN-27'),
    ('l10n_vn.state_vn_VN-28', 'base.state_vn_VN-28'),
    ('l10n_vn.state_vn_VN-29', 'base.state_vn_VN-29'),
    ('l10n_vn.state_vn_VN-30', 'base.state_vn_VN-30'),
    ('l10n_vn.state_vn_VN-31', 'base.state_vn_VN-31'),
    ('l10n_vn.state_vn_VN-32', 'base.state_vn_VN-32'),
    ('l10n_vn.state_vn_VN-33', 'base.state_vn_VN-33'),
    ('l10n_vn.state_vn_VN-34', 'base.state_vn_VN-34'),
    ('l10n_vn.state_vn_VN-35', 'base.state_vn_VN-35'),
    ('l10n_vn.state_vn_VN-36', 'base.state_vn_VN-36'),
    ('l10n_vn.state_vn_VN-37', 'base.state_vn_VN-37'),
    ('l10n_vn.state_vn_VN-39', 'base.state_vn_VN-39'),
    ('l10n_vn.state_vn_VN-40', 'base.state_vn_VN-40'),
    ('l10n_vn.state_vn_VN-41', 'base.state_vn_VN-41'),
    ('l10n_vn.state_vn_VN-43', 'base.state_vn_VN-43'),
    ('l10n_vn.state_vn_VN-44', 'base.state_vn_VN-44'),
    ('l10n_vn.state_vn_VN-45', 'base.state_vn_VN-45'),
    ('l10n_vn.state_vn_VN-46', 'base.state_vn_VN-46'),
    ('l10n_vn.state_vn_VN-47', 'base.state_vn_VN-47'),
    ('l10n_vn.state_vn_VN-49', 'base.state_vn_VN-49'),
    ('l10n_vn.state_vn_VN-50', 'base.state_vn_VN-50'),
    ('l10n_vn.state_vn_VN-51', 'base.state_vn_VN-51'),
    ('l10n_vn.state_vn_VN-52', 'base.state_vn_VN-52'),
    ('l10n_vn.state_vn_VN-53', 'base.state_vn_VN-53'),
    ('l10n_vn.state_vn_VN-54', 'base.state_vn_VN-54'),
    ('l10n_vn.state_vn_VN-55', 'base.state_vn_VN-55'),
    ('l10n_vn.state_vn_VN-56', 'base.state_vn_VN-56'),
    ('l10n_vn.state_vn_VN-57', 'base.state_vn_VN-57'),
    ('l10n_vn.state_vn_VN-58', 'base.state_vn_VN-58'),
    ('l10n_vn.state_vn_VN-59', 'base.state_vn_VN-59'),
    ('l10n_vn.state_vn_VN-61', 'base.state_vn_VN-61'),
    ('l10n_vn.state_vn_VN-63', 'base.state_vn_VN-63'),
    ('l10n_vn.state_vn_VN-66', 'base.state_vn_VN-66'),
    ('l10n_vn.state_vn_VN-67', 'base.state_vn_VN-67'),
    ('l10n_vn.state_vn_VN-68', 'base.state_vn_VN-68'),
    ('l10n_vn.state_vn_VN-69', 'base.state_vn_VN-69'),
    ('l10n_vn.state_vn_VN-70', 'base.state_vn_VN-70'),
    ('l10n_vn.state_vn_VN-71', 'base.state_vn_VN-71'),
    ('l10n_vn.state_vn_VN-72', 'base.state_vn_VN-72'),
    ('l10n_vn.state_vn_VN-73', 'base.state_vn_VN-73'),
    ('l10n_vn.state_vn_VN-CT', 'base.state_vn_VN-CT'),
    ('l10n_vn.state_vn_VN-DN', 'base.state_vn_VN-DN'),
    ('l10n_vn.state_vn_VN-HN', 'base.state_vn_VN-HN'),
    ('l10n_vn.state_vn_VN-HP', 'base.state_vn_VN-HP'),
    ('l10n_vn.state_vn_VN-SG', 'base.state_vn_VN-SG'),
]

xmlid_renames_ir_module_category = [
    ("base.module_category_accounting_and_finance",
     "base.module_category_accounting_accounting"),
    ("base.module_category_administration",
     "base.module_category_administration_administration"),
    ("base.module_category_crm", "base.module_category_sales_crm"),
    ("base.module_category_event_management",
     "base.module_category_marketing_events"),
    ("base.module_category_helpdesk",
     "base.module_category_operations_helpdesk"),
    ("base.module_category_hr_appraisal",
     "base.module_category_human_resources_appraisals"),
    ("base.module_category_hr_attendance",
     "base.module_category_human_resources_attendances"),
    ("base.module_category_hr_contract",
     "base.module_category_human_resources_contracts"),
    ("base.module_category_hr_expense",
     "base.module_category_accounting_expenses"),
    ("base.module_category_hr_holidays",
     "base.module_category_human_resources_time_off"),
    ("base.module_category_hr_recruitment",
     "base.module_category_human_resources_recruitment"),
    ("base.module_category_hr_timesheet",
     "base.module_category_operations_timesheets"),
    ("base.module_category_human_resources",
     "base.module_category_human_resources_employees"),
    ("base.module_category_manufacturing",
     "base.module_category_manufacturing_manufacturing"),
    ("base.module_category_mass_mailing",
     "base.module_category_marketing_email_marketing"),
    ("base.module_category_payment_acquirer",
     "base.module_category_accounting_payment"),
    ("base.module_category_point_of_sale",
     "base.module_category_sales_point_of_sale"),
    ("base.module_category_project_management",
     "base.module_category_operations_project"),
    ("base.module_category_purchase_management",
     "base.module_category_operations_purchase"),
    ("base.module_category_sales_management",
     "base.module_category_sales_sales"),
    ("base.module_category_sign", "base.module_category_sales_sign"),
    ("base.module_category_stock",
     "base.module_category_operations_inventory_delivery"),
    ("base.module_category_survey",
     "base.module_category_marketing_survey"),
    ("base.module_category_warehouse_management",
     "base.module_category_operations_inventory"),
    ("base.module_category_website",
     "base.module_category_website_website"),
    ("fleet.module_fleet_category",
     "base.module_category_human_resources_fleet"),
    ("im_livechat.module_category_im_livechat",
     "base.module_category_website_live_chat"),
    ("lunch.module_lunch_category",
     "base.module_category_human_resources_lunch"),
]

xmlid_renames_ir_model_access = [
    ('web.access_report_layout', 'base.access_report_layout'),
]

lang_code_renames = [
    ('ar_AA', 'ar_001'),
    ('fil', 'fil_PH'),
]

column_copies = {
    "ir_actions": [("binding_type", None, None)],
}

column_renames = {
    'ir_act_window': [
        ("multi", None)
    ],
    'ir_model_fields': [
        ('selection', None),
    ],
    'ir_attachment': [
        ('name', None),
        ('datas_fname', 'name'),
        ("res_name", None)
    ],
    'res_lang': [
        ('week_start', None),
    ],
    'res_partner': [
        ("customer", None),
        ("supplier", None)
    ],
}

field_renames = [
    ('ir.server.object.lines',
     'ir_server_object_lines',
     'type', 'evaluation_type'),
]

_obsolete_tables = (
    "account_invoice",
    "account_invoice_import_wizard",
    "account_invoice_line",
    "account_invoice_tax",
    "account_voucher",
    "account_voucher_line",
    "lunch_order_line",
    "mail_mass_mailing_campaign"
    "slide_category",
    "survey_page",
    "account_analytic_tag_account_invoice_line_rel",
    "account_analytic_tag_account_invoice_tax_rel",
    "account_invoice_account_move_line_rel",
    "account_invoice_import_wizard_ir_attachment_rel",
    "account_invoice_line_tax",
    "account_invoice_payment_rel",
    "sale_order_line_invoice_rel",
    "summary_dept_rel",
    "project_task_assign_so_line_rel",
    "mail_mass_mailing_tag_rel",
)


def fix_lang_table(cr):
    """Avoid error on normal update process due to changed language codes"""
    for old_code, new_code in lang_code_renames:
        openupgrade.logged_query(
            cr,
            "UPDATE res_lang SET code=%s WHERE code=%s",
            (new_code, old_code)
        )


def fix_country_state_xml_id_on_existing_records(cr):
    """Suppose you have country states introduced manually.
    This method ensure you don't have problems later in the migration when
    loading the res.country.state.csv"""
    with open(get_module_resource('base', 'data', 'res.country.state.csv'),
              'r') as country_states_file:
        states = csv.reader(country_states_file, delimiter=',', quotechar='"')
        _ = next(states)
        for row in states:
            state_xml_id, country_xml_id, _, state_code = row
            # find if csv record exists in ir_model_data
            cr.execute(
                """SELECT rcs.id, imd_rcs.id
                FROM res_country_state rcs
                INNER JOIN res_country rc ON rcs.country_id = rc.id
                INNER JOIN ir_model_data imd_rc ON (
                    imd_rc.res_id = rc.id AND
                    imd_rc.model = 'res.country' AND
                    imd_rc.module = 'base' AND
                    imd_rc.name = %(country_xml_id)s
                )
                LEFT JOIN ir_model_data imd_rcs ON (
                    imd_rcs.res_id = rcs.id AND
                    imd_rcs.model = 'res.country.state' AND
                    imd_rcs.module = 'base' AND
                    imd_rcs.name = %(state_xml_id)s
                )
                WHERE rcs.code = %(state_code)s""", {
                    "country_xml_id": country_xml_id,
                    "state_code": state_code,
                    "state_xml_id": state_xml_id,
                }
            )
            row = cr.fetchone()
            if not row:  # non existing record - It will be created later
                continue
            if not row[1]:  # Unexisting XML-ID - Create it
                openupgrade.add_xmlid(
                    cr, "base", state_xml_id, "res.country.state", row[0])


def remove_invoice_table_relations(env):
    # for custom modules that have many2many relations to invoice models
    openupgrade.logged_query(
        env.cr, """
        DELETE FROM ir_model_relation imr
        USING ir_model im
        WHERE imr.model = im.id AND im.model IN (
            'account.invoice',
            'account.invoice.import.wizard',
            'account.invoice.line',
            'account.invoice.tax',
            'account.voucher',
            'account.voucher.line')""",
    )


def fill_ir_model_data_noupdate(env):
    """In previous version, true noupdate data by default was saved as null.
    See https://github.com/odoo/odoo/commit/8f88570ca18061716fd6e246b9d16aa2cbc24f3a"""
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_model_data
        SET noupdate = TRUE
        WHERE noupdate IS NULL AND model != 'ir.model'"""
    )
    # In Odoo 13.0, ir.model xmlids are noupdate FALSE instead of NULL and are
    # thus included when cleaning up obsolete data records in _process_end.
    openupgrade.logged_query(
        env.cr,
        """UPDATE ir_model_data
        SET noupdate=FALSE
        WHERE model='ir.model' AND noupdate IS NULL""")


def remove_offending_translations(env):
    """Remove translations that has changed its way of working (constraint,
    sql_constraint and selection), as there's no easy way to convert them,
    and leaving them will lead to "selection value not valid" errors.
    """
    openupgrade.logged_query(
        env.cr,
        "DELETE FROM ir_translation WHERE type IN "
        "('constraint', 'sql_constraint', 'selection')",
    )


def handle_web_favicon_module(env):
    """If web_favicon is installed in previous version, we can reuse
    that icon for the native favicon feature.
    """
    if openupgrade.column_exists(env.cr, "res_company", "favicon_backend"):
        openupgrade.rename_fields(
            env,
            [("res.company", "res_company", "favicon_backend", "favicon")],
            no_deep=True,
        )


def add_res_lang_url_code(env):
    """Add field and filled it with same logic as core (iso_code or code)."""
    openupgrade.add_fields(
        env, [("url_code", "res.lang", "res_lang", "char", False, "base")]
    )
    openupgrade.logged_query(
        env.cr, "UPDATE res_lang SET url_code = COALESCE(iso_code, code)"
    )


def switch_noupdate_records(env):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "base",
        [
            "module_category_accounting_accounting",
            "module_category_marketing_events",
            "module_category_human_resources_attendances",
            "module_category_human_resources_contracts",
            "module_category_accounting_expenses",
            "module_category_human_resources_time_off",
            "module_category_human_resources_recruitment",
            "module_category_operations_timesheets",
            "module_category_marketing_email_marketing",
            "module_category_operations_project",
            "module_category_operations_purchase",
            "module_category_sales_sales",
            "module_category_marketing_survey",
            "module_category_operations_inventory",
            "module_category_human_resources_fleet",
            "module_category_website_live_chat",
            "module_category_human_resources_lunch",
        ],
        True,
    )
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "base",
        [
            "state_DO_01",
            "state_DO_02",
            "state_DO_03",
            "state_DO_04",
            "state_DO_05",
            "state_DO_06",
            "state_DO_07",
            "state_DO_08",
            "state_DO_09",
            "state_DO_10",
            "state_DO_11",
            "state_DO_12",
            "state_DO_13",
            "state_DO_14",
            "state_DO_15",
            "state_DO_16",
            "state_DO_17",
            "state_DO_18",
            "state_DO_19",
            "state_DO_20",
            "state_DO_21",
            "state_DO_22",
            "state_DO_23",
            "state_DO_24",
            "state_DO_25",
            "state_DO_26",
            "state_DO_27",
            "state_DO_28",
            "state_DO_29",
            "state_DO_30",
            "state_DO_31",
            "state_DO_32",
        ],
        False,
    )


def rename_ir_module_category(env):
    for old_xmlid, new_xmlid in xmlid_renames_ir_module_category:
        module, name = new_xmlid.split('.')
        sql = "SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s"
        env.cr.execute(sql, (module, name))
        new_row = env.cr.fetchone()
        module, name = old_xmlid.split('.')
        env.cr.execute(sql, (module, name))
        old_row = env.cr.fetchone()
        if old_row:
            if new_row:
                query = "SELECT parent_id FROM ir_module_category WHERE id = %s"
                env.cr.execute(query, (new_row[0], ))
                new_parent_row = env.cr.fetchone()
                if new_parent_row and new_parent_row[0] == old_row[0]:
                    # When we already have recursive categories with same name
                    # (example: Manufacturing/Manufacturing), doing a merge let
                    # the akward situation where the parent points to itself,
                    # so we avoid it checking this condition
                    continue
                openupgrade_merge_records.merge_records(
                    env, "ir.module.category", [old_row[0]], new_row[0],
                    method="sql", model_table="ir_module_category")
            else:
                openupgrade.rename_xmlids(env.cr, [(old_xmlid, new_xmlid)])


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.remove_tables_fks(env.cr, _obsolete_tables)
    remove_invoice_table_relations(env)
    # Deactivate the noupdate flag (hardcoded on initial SQL load) for allowing
    # to update changed data on this group.
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_model_data SET noupdate=False
        WHERE module='base' AND name='group_user'""",
    )
    openupgrade.update_module_names(
        env.cr, apriori.renamed_modules.items())
    openupgrade.update_module_names(
        env.cr, apriori.merged_modules.items(), merge_modules=True)
    openupgrade.copy_columns(env.cr, column_copies)
    openupgrade.rename_columns(env.cr, column_renames)
    openupgrade.rename_fields(env, field_renames, no_deep=True)
    openupgrade.rename_xmlids(env.cr, xmlid_renames_res_country_state)
    openupgrade.rename_xmlids(env.cr, xmlid_renames_ir_model_access)
    fill_ir_model_data_noupdate(env)
    fix_lang_table(env.cr)
    fix_country_state_xml_id_on_existing_records(env.cr)
    remove_offending_translations(env)
    handle_web_favicon_module(env)
    add_res_lang_url_code(env)
    rename_ir_module_category(env)
    switch_noupdate_records(env)
    openupgrade.logged_query(
        env.cr,
        """ UPDATE ir_model_constraint
        SET create_date = date_init
        WHERE create_date IS NULL AND date_init IS NOT NULL """)
    openupgrade.logged_query(
        env.cr,
        """ UPDATE ir_model_constraint
        SET write_date = date_update
        WHERE write_date IS NULL AND date_update IS NOT NULL """)
