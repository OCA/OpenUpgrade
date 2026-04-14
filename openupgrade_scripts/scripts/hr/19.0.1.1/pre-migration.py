# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

renamed_fields = [
    ("hr.employee", "hr_employee", "gender", "sex"),
]

renamed_fields_hr_contract = [
    ("hr.contract", "hr_contract", "date_start", "contract_date_start"),
    ("hr.contract", "hr_contract", "date_end", "contract_date_end"),
]

renamed_field_references = [
    ("hr.employee", "bank_account_id", "bank_account_ids"),
]

added_fields = [
    (
        "country_id",
        "hr.departure.reason",
        "hr_departure_reason",
        "many2one",
        None,
        "hr",
    ),
    ("employee", "res.partner", "res_partner", "boolean", None, "hr", False),
]

renamed_tables_hr_contract = [
    ("hr_contract", "hr_version"),
]

renamed_models = [
    ("hr.contract", "hr.version"),
]

renamed_xmlids = [
    ("hr.contract_type_statutaire", "hr.contract_type_statutory"),
]

deleted_xmlids = [
    "hr.ir_cron_data_check_work_permit_validity",
    "hr.ir_cron_data_contract_update_state",
    "hr.ir_rule_hr_contract_employee_manager",
    "hr.ir_rule_hr_contract_history_multi_company",
    "hr_contract.group_hr_contract_employee_manager",
    "hr_contract.group_hr_contract_manager",
]


def res_partner_employee(env):
    """
    Compute res.partner#employee
    """
    env.cr.execute(
        """
        UPDATE res_partner
        SET
        employee=True
        FROM
        hr_employee
        WHERE
        hr_employee.work_contact_id=res_partner.id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, renamed_fields)
    openupgrade.rename_field_references(env, renamed_field_references)
    openupgrade.add_fields(env, added_fields)
    openupgrade.rename_xmlids(env.cr, renamed_xmlids)
    openupgrade.delete_records_safely_by_xml_id(env, deleted_xmlids)
    if openupgrade.table_exists(env.cr, "hr_contract"):
        openupgrade.rename_fields(env, renamed_fields_hr_contract)
        openupgrade.rename_tables(env.cr, renamed_tables_hr_contract)
        openupgrade.rename_models(env.cr, renamed_models)
    res_partner_employee(env)
