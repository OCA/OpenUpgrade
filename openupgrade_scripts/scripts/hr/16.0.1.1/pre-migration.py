# Copyright 2023 Coop IT Easy (https://coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    (
        "hr_contract.access_hr_contract_type_manager",
        "hr.access_hr_contract_type_manager",
    ),
]

_new_fields = [
    (
        "company_id",  # field name
        "hr.plan",  # module name
        False,  # SQL table name
        "many2one",  # field type
        False,  # SQL field type
        "hr",  # module name
    ),
    (
        "company_id",  # field name
        "hr.plan.activity.type",  # module name
        False,  # SQL table name
        "many2one",  # field type
        False,  # SQL field type
        "hr",  # module name
    ),
    (
        "master_department_id",  # field name
        "hr.department",  # module name
        False,  # SQL table name
        "many2one",  # field type
        False,  # SQL field type
        "hr",  # module name
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.add_fields(env, _new_fields)
    # Backup Many2many relation between hr.plan and hr.plan.activity.type
    openupgrade.remove_tables_fks(env.cr, ["hr_plan_hr_plan_activity_type_rel"])
    # get_legacy_name cannot be used here, as there is a length limit in table name,
    # and it causes a conflict. Waiting for a fix in
    # openupgradelib, we will use a new table name here.
    openupgrade.rename_tables(
        env.cr,
        [
            (
                "hr_plan_hr_plan_activity_type_rel",
                "ou_legacy_16_0_hr_plan_hr_plan_activity_type_rel",
            )
        ],
    )
