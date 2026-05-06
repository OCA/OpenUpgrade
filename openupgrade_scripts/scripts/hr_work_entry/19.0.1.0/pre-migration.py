# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

renamed_xmlids = [
    (
        "hr_work_entry.overtime_work_entry_type",
        "hr_work_entry.work_entry_type_overtime",
    ),
]

noupdate_xmlids = [
    "work_entry_type_attendance",
    "work_entry_type_compensatory",
    "work_entry_type_home_working",
    "work_entry_type_leave",
    "work_entry_type_legal_leave",
    "work_entry_type_sick_leave",
    "work_entry_type_unpaid_leave",
]


def hr_work_entry(env):
    """
    Set hr.work.entry#version_id from contract_id or latest version,
    hr.work.entry#amount_rate=1,
    hr.work.entry#date
    """
    openupgrade.add_fields(
        env,
        [
            (
                "version_id",
                "hr.work.entry",
                "hr_work_entry",
                "many2one",
                None,
                "hr_work_entry",
            ),
            (
                "amount_rate",
                "hr.work.entry",
                "hr_work_entry",
                "float",
                None,
                "hr_work_entry",
                1.0,
            ),
            ("date", "hr.work.entry", "hr_work_entry", "date", None, "hr_work_entry"),
        ],
    )
    if openupgrade.column_exists(env.cr, "hr_work_entry", "contract_id"):
        env.cr.execute(
            f"""
            UPDATE hr_work_entry
            SET version_id=hr_version.id
            FROM hr_version
            WHERE
            hr_version.{openupgrade.get_legacy_name("contract_id")}=hr_work_entry.contract_id
            """
        )
    env.cr.execute(
        """
        UPDATE hr_work_entry
        SET version_id=employee2version.version_id
        FROM (
            SELECT employee_id, max(id) version_id
            FROM hr_version
            GROUP BY employee_id
        ) employee2version
        WHERE
        employee2version.employee_id=hr_work_entry.employee_id
        AND
        hr_work_entry.version_id IS NULL
        """
    )
    env.cr.execute(
        """
        WITH employee2tz AS (
            SELECT
            hr_employee.id employee_id,
            COALESCE(resource_resource.tz, resource_calendar.tz, res_partner.tz) tz
            FROM hr_employee
            JOIN resource_resource ON hr_employee.resource_id=resource_resource.id
            LEFT JOIN resource_calendar
                ON resource_resource.calendar_id=resource_calendar.id
            JOIN res_company ON hr_employee.company_id=res_company.id
            JOIN res_partner ON res_company.partner_id=res_partner.id
        )
        UPDATE hr_work_entry
        SET
        date=(date_start at time zone employee2tz.tz)::date
        FROM employee2tz
        WHERE employee2tz.employee_id=hr_work_entry.employee_id
        AND date_start IS NOT NULL
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, renamed_xmlids)
    openupgrade.set_xml_ids_noupdate_value(env, "hr_work_entry", noupdate_xmlids, True)
    openupgrade.delete_sql_constraint_safely(
        env, "hr_work_entry", "hr_work_entry", "work_entries_no_validated_conflict"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "hr_work_entry", "hr_work_entry", "work_entry_has_end"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "hr_work_entry", "hr_work_entry", "work_entry_start_before_end"
    )
    hr_work_entry(env)
