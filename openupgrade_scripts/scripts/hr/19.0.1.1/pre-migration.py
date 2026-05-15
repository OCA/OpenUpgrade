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


# Fields added to hr.employee by the 18.0 hr_contract module that no longer
# exist anywhere in 19.0 (verified: not defined on hr.employee, hr.version,
# hr.employee.public, or any hr* module). They're listed in
# upgrade_analysis_work.txt under the hr_contract → hr.employee DEL block
# (lines 256-259) which is annotated "# NOTHING TO DO" — but in practice the
# stale ir_model_fields rows + ir_ui_view records referencing these fields
# trip cross-cutting view validation when later modules' data loads
# (reproduced on `l10n_ae/data/account_tax_report_data.xml:3` with the error
# `Field 'first_contract_date' does not exist in model 'hr.employee'`).
# The analysis underreported the DELs — it listed 5 of the 10 stale fields.
_obsolete_hr_employee_fields = (
    "contract_id",
    "contract_ids",
    "contract_template_id",
    "contract_type_id",
    "contract_wage",
    "contract_warning",
    "contracts_count",
    "first_contract_date",
    "is_in_contract",
    "vehicle",
)


def cleanup_obsolete_hr_employee_fields(env):
    """
    Delete stale ir_model_fields rows + orphan views for fields the 18.0
    hr_contract module added to hr.employee/hr.employee.public that are
    removed in 19.0. The migration framework does not sweep these
    automatically when the donor module is merged via apriori.
    """
    # Build the list of xml_ids for the obsolete field metadata on both
    # hr.employee and hr.employee.public.
    field_xmlids = [
        f"hr.field_hr_employee__{name}" for name in _obsolete_hr_employee_fields
    ] + [
        f"hr.field_hr_employee_public__{name}" for name in _obsolete_hr_employee_fields
    ]

    # Delete orphan views (on hr.employee and hr.employee.public) whose
    # arch_db references any of these field names with the standard
    # <field name="X"/> pattern. Done before the field rows themselves so
    # the migration data load can re-create the proper 19.0 views.
    patterns = "|".join(
        f'name=\\\\"{name}\\\\"' for name in _obsolete_hr_employee_fields
    )
    env.cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE model = 'ir.ui.view'
        AND res_id IN (
            SELECT v.id FROM ir_ui_view v
            WHERE v.model IN ('hr.employee', 'hr.employee.public')
              AND v.arch_db::text ~ %s
        )
        """,
        (patterns,),
    )
    env.cr.execute(
        """
        DELETE FROM ir_ui_view
        WHERE model IN ('hr.employee', 'hr.employee.public')
          AND arch_db::text ~ %s
        """,
        (patterns,),
    )

    # Delete the stale field xml_ids + their underlying ir_model_fields rows.
    openupgrade.delete_records_safely_by_xml_id(env, field_xmlids)


def cleanup_openupgrade_renamed_hr_views(env):
    """
    Delete orphan ir_ui_view records that openupgradelib renamed with an
    `_openupgrade_<id>` suffix during the hr_contract → hr apriori merge
    (openupgradelib.openupgrade.update_module_names auto-renames xml_ids
    that would otherwise collide when changing module ownership).

    The renamed views are guaranteed orphans because their original
    18.0 xml_id no longer has a matching source XML in 19.0 hr — they're
    leftovers from views that 19.0 has either dropped or rewritten under
    a different xml_id. Their arch_db still references 18.0-only fields
    or xpath targets (e.g. //block[@name='employee_rights_setting_container']
    in res.config.settings) and trips view-inheritance resolution when
    later modules' data XML loads (reproduced on
    l10n_ae/data/account_tax_report_data.xml:3 with the error
    'Element ... cannot be located in parent view').
    """
    env.cr.execute(
        """
        DELETE FROM ir_ui_view
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = 'hr'
              AND model = 'ir.ui.view'
              AND name LIKE '%%_openupgrade_%%'
        )
        """
    )
    env.cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE module = 'hr'
          AND model = 'ir.ui.view'
          AND name LIKE '%%_openupgrade_%%'
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
    cleanup_obsolete_hr_employee_fields(env)
    cleanup_openupgrade_renamed_hr_views(env)
    res_partner_employee(env)
