# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "hr.dep_sales",
    "hr.openupgrade_legacy_17_0_offboarding_plan",
    "hr.openupgrade_legacy_17_0_onboarding_plan",
    "hr.openupgrade_legacy_17_0_offboarding_setup_compute_out_delais",
    "hr.openupgrade_legacy_17_0_offboarding_take_back_hr_materials",
    "hr.openupgrade_legacy_17_0_onboarding_plan_training",
    "hr.openupgrade_legacy_17_0_onboarding_setup_it_materials",
    "hr.openupgrade_legacy_17_0_onboarding_training",
    "hr.hr_plan_activity_type_company_rule",
    "hr.hr_plan_company_rule",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr", "17.0.1.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
